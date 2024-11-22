import torch
from torch import nn

class UnetBlock(nn.Module):
    """
    A single block of the U-Net model. U-Net is used for image processing tasks, 
    especially for segmenting and colorizing images.
    """
    def __init__(self, nf, ni, submodule=None, input_c=None, dropout=False,
                 innermost=False, outermost=False):
        """
        Initialize the U-Net block.
        
        Parameters
        ----------
        nf : int
            Number of filters in the output.
        ni : int
            Number of filters in the input.
        submodule : nn.Module, optional
            Another U-Net block that this block will use.
        input_c : int, optional
            Number of input channels. Defaults to nf.
        dropout : bool, optional
            Whether to apply dropout (a way to prevent overfitting).
        innermost : bool, optional
            If True, this is the innermost block of the U-Net.
        outermost : bool, optional
            If True, this is the outermost block of the U-Net.
        """
        super().__init__()
        self.outermost = outermost  # Mark this block as the outermost one

        if input_c is None:
            input_c = nf  # Set the input channels to the number of output filters

        # Define the layers for this block
        downconv = nn.Conv2d(input_c, ni, kernel_size=4, stride=2, padding=1, bias=False)
        downrelu = nn.LeakyReLU(0.2, True)
        downnorm = nn.BatchNorm2d(ni)
        uprelu = nn.ReLU(True)
        upnorm = nn.BatchNorm2d(nf)

        if outermost:
            # If this is the outermost block, it does not need concatenation
            upconv = nn.ConvTranspose2d(ni * 2, nf, kernel_size=4, stride=2, padding=1)
            down = [downconv]  # Only downconv for outermost block
            up = [uprelu, upconv, nn.Tanh()]  # Upconv, relu, and tanh for outermost block
            model = down + [submodule] + up  # Combine everything to make the full block
        elif innermost:
            # If this is the innermost block, it does not have a submodule
            upconv = nn.ConvTranspose2d(ni, nf, kernel_size=4, stride=2, padding=1, bias=False)
            down = [downrelu, downconv]  # Relu and downconv for innermost block
            up = [uprelu, upconv, upnorm]  # Upconv, relu, and norm for innermost block
            model = down + up  # Combine layers for the innermost block
        else:
            # Regular block with both down and up layers
            upconv = nn.ConvTranspose2d(ni * 2, nf, kernel_size=4, stride=2, padding=1, bias=False)
            down = [downrelu, downconv, downnorm]  # Relu, downconv, and norm for regular block
            up = [uprelu, upconv, upnorm]  # Relu, upconv, and norm for regular block
            if dropout:
                up += [nn.Dropout(0.5)]  # Add dropout if needed
            model = down + [submodule] + up  # Combine layers and submodule

        self.model = nn.Sequential(*model)  # Create a sequential model with the defined layers

    def forward(self, x):
        """
        Forward pass through the U-Net block.
        
        Parameters
        ----------
        x : torch.Tensor
            The input image tensor.
        
        Returns
        -------
        torch.Tensor
            The output image tensor.
        """
        if self.outermost:
            return self.model(x)  # For the outermost block, just return the model output
        else:
            return torch.cat([x, self.model(x)], 1)  # For other blocks, concatenate input and output (skip connection)
        
class Unet(nn.Module):
    """
    U-Net model for tasks like image segmentation and colorization.
    """
    def __init__(self, input_c=1, output_c=2, n_down=8, num_filters=64):
        """
        Initialize the U-Net model.
        
        Parameters
        ----------
        input_c : int
            Number of input channels (e.g., 1 for grayscale).
        output_c : int
            Number of output channels (e.g., 2 for color).
        n_down : int
            Number of downsampling steps.
        num_filters : int
            Number of filters in the first layer.
        """
        super().__init__()
        
        # Start with the innermost block of the U-Net
        unet_block = UnetBlock(num_filters * 8, num_filters * 8, innermost=True)
        
        # Add more blocks to the U-Net
        for _ in range(n_down - 5):
            unet_block = UnetBlock(num_filters * 8, num_filters * 8, submodule=unet_block, dropout=True)
        
        # Create the rest of the blocks
        out_filters = num_filters * 8
        for _ in range(3):
            unet_block = UnetBlock(out_filters // 2, out_filters, submodule=unet_block)
            out_filters //= 2
        
        # Create the outermost block
        self.model = UnetBlock(output_c, out_filters, input_c=input_c, submodule=unet_block, outermost=True)

    def forward(self, x):
        """
        Forward pass through the U-Net model.
        
        Parameters
        ----------
        x : torch.Tensor
            The input image tensor.
        
        Returns
        -------
        torch.Tensor
            The output image tensor.
        """
        return self.model(x)