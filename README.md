# RESPONSIVE IMAGE GENERATOR
## DESCRIPTION
This python module uses the pillow package to generate the responsive images of different sizes.

## EXAMPLES
```
from respimagenpy.generate import ResponsiveImageGenerator

sizes = [
    # Mobile devices
    { "rename": True, "name": "sm", "suffix": "_1x", "quality": 100, "width": 320 },
    # Mobile devices, iPads, Tablets
    { "rename": True, "name": "sm", "suffix": "_2x", "quality": 100, "width": 481 },
    # iPads, Tablets
    { "rename": True, "name": "md", "suffix": "_1x", "quality": 100, "width": 769 },
    # iPads, Tablets, Desktops, large screens
    { "rename": True, "name": "md", "suffix": "_2x", "quality": 100, "width": 1025 },
    # Desktops, large screens
    { "rename": True, "name": "lg", "suffix": "_1x", "quality": 100, "width": 1201 },
    # Extra large screens, TV
    { "rename": True, "name": "lg", "suffix": "_2x", "quality": 100, "width": 1440 },
    # Extra large screens, TV (HD)
    { "rename": True, "name": "xl", "suffix": "_1x", "quality": 100, "width": 1920 },
    # Extra large screens, TV (UHD)
    # { "name": "xl", "suffix": "_2x", "quality": 100, "width": 3820 },
]

SOURCE = "C:\\images\"

generator = ResponsiveImageGenerator(SOURCE, params=sizes)
generator.execute()
```
