"""
Package: Generate
Description: This package gives helper classes and methods to generate
            Responsive Image Sizes which you can include in your websites
            for better load time.
"""
import os
import sys
from pathlib import Path
import logging
import threading
from PIL import Image
import PIL
from genericpath import isdir


class ResponsiveImageGenerator():
    """
    Main Class which facilitates generation of different sizes of image.
    """
    params_list:list = []
    src:str = "src"
    dest:str = "dest"
    opt_format:str = "webp"
    extensions = ('.jpg', '.png', '.JPG', '.PNG')
    thumbnail_size:tuple = (300,300)
    logger = None

    def __init__(self, src, params, logger=None):
        self.src = src
        self.params_list = params
        if logger is None:
            self.set_logger()

    def set_logger(self):
        """
        Setting up logger for the package
        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        f_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s', '%m-%d-%Y %H:%M:%S'
        )
        debug_handler =  logging.FileHandler(f'{__name__}.log')
        debug_handler.setLevel(logging.INFO)
        debug_handler.setFormatter(f_format)

        stdout_handler =  logging.StreamHandler(sys.stdout)
        stdout_handler.setLevel(logging.DEBUG)
        stdout_handler.setFormatter(f_format)

        self.logger.addHandler(stdout_handler)
        self.logger.addHandler(debug_handler)

    def checkdirs(self):
        """Checks the source directory exists

        Raises:
            FileNotFoundError: _description_
            Exception: _description_

        """
        if not isdir(self.src):
            raise FileNotFoundError(f"{self.src}: Directory does not exist")
        return False

    def scandir(self, directory:str, counter:int):
        """Finds all files in a given directory recursively

        Args:
            dir (str): _description_
            ext (list): _description_

        Returns:
            list: [subfolders, files]
        """
        subfolders, files = [], []

        for _f in os.scandir(directory):
            if _f.is_dir():
                subfolders.append(_f.path)
            if _f.is_file():
                if os.path.splitext(_f.name)[1].lower() in self.extensions:
                    # files.append(_f.path)
                    self.generate_in_parallel(_f.path, counter)
                    counter += 1

        for _d in list(subfolders):
            _sf, _f = self.scandir(_d, counter)
            subfolders.extend(_sf)
            files.extend(_f)

        return subfolders, files

    def get_images(self):
        """Get all images in the src directory

        Returns:
            list: list of image file names
        """
        return [
            file for file in os.listdir(self.src) if file.endswith(self.extensions)
        ]

    def find_height(self, size, _dw=None, _dh=None):
        """Finds the correct height to be used for resize

        Args:
            size (int, int): Size of the actual image
            dw (int, optional): Destination Width. Defaults to None.
            dh (int, optional): Destination Height. Defaults to None.

        Raises:
            Exception: Destination Width or Height is mandatory
            DivideByZero

        Returns:
            tuple: (Width, Height)
        """
        _sw, _sh = size
        wpercent = None
        hpercent = None
        if _dw is not None:
            wpercent = _dw/_sw if _sw > _dw else _sw/_dw
        elif _dh is not None:
            hpercent = _dh/_sh if _sh > _dh else _sh/_dh
        else:
            raise Exception("Destination Width or Height is mandatory")
        _dh = _sh*wpercent if wpercent is not None else _dh
        _dw = _sw*hpercent if hpercent is not None else _dw
        return int(_dw),int(_dh)

    def check_source_files(self):
        """
        Finds all convertible image files in source directory and prepare to
        process them
        """
        return self.scandir(self.src, 1)

    def generate_in_parallel(self, image, counter):
        """
        Generate the file in desired size given as argument
        """
        if image is None:
            raise Exception("Image can not be empty")
        try:
            self.logger.info("Processing %s", image)
            self.generate_thumbnail(image,counter)
            name_without_ext, _ = image.split(".")
            for params in self.params_list:
                self.logger.info("Generating responsive image @%sw", params['width'])
                if params['rename'] is False:
                    qualified_name = name_without_ext
                else:
                    parent_dir = Path(name_without_ext).resolve().parent
                    qualified_name = os.path.join(parent_dir, f"{counter:05d}")
                qualified_name += f"@{params['name']}{params['suffix']}"
                qualified_name += f".{self.opt_format}"
                img = Image.open(image)
                size = self.find_height(img.size, params['width'])
                img = img.resize(size, PIL.Image.ANTIALIAS)
                img = self.transpose_if_required(img)
                img.save(qualified_name, format=self.opt_format,
                            optimize=True, quality=params['quality'])
            counter += 1
        #pylint: disable=broad-except
        except Exception as error:
            self.logger.error(error)
            # raise Exception(error)

    def generate_thumbnail(self, img_p, name, size=None):
        """Generates thumbnail for the given size.

        Args:
            size (width:int, height:int): Thumbnail width and height.
                Defaults to None.
        """
        if size is not None:
            self.thumbnail_size = size

        try:
            self.logger.info("Generating thumbnail")
            name_without_ext, _ = img_p.split(".")
            if name is not None:
                parent_dir = Path(name_without_ext).resolve().parent
                name_without_ext = os.path.join(parent_dir, f"{name:05d}")
            qualified_name = f"{name_without_ext}@thumbnail.{self.opt_format}"
            img = Image.open(img_p)
            img.thumbnail(size=self.thumbnail_size)
            img = self.transpose_if_required(img)
            img.save(qualified_name, format=self.opt_format, optimize=True, quality=100)
        #pylint: disable=broad-except
        except Exception as error:
            self.logger.error(":".join([str(error), img_p]))
            # raise Exception(e)

    def transpose_if_required(self, image):
        """Transpose image if required.

        Args:
            image: input image to be transposed
        returns:
            Image
        """
        try:
            image_exif = image.getexif()
            image_orientation = image_exif[274]
            self.logger.debug("Orientation of an Image: %s", image_orientation)
            if image_orientation in (2,'2'):
                image = image.transpose(Image.FLIP_LEFT_RIGHT)
            elif image_orientation in (3,'3'):
                image = image.transpose(Image.ROTATE_180)
            elif image_orientation in (4,'4'):
                image = image.transpose(Image.FLIP_TOP_BOTTOM)
            elif image_orientation in (5,'5'):
                image = image.transpose(Image.ROTATE_90).transpose(Image.FLIP_TOP_BOTTOM)
            elif image_orientation in (6,'6'):
                image = image.transpose(Image.ROTATE_270)
            elif image_orientation in (7,'7'):
                image = image.transpose(Image.ROTATE_270).transpose(Image.FLIP_TOP_BOTTOM)
            elif image_orientation in (8,'8'):
                image = image.transpose(Image.ROTATE_90)
            else:
                pass
        except (KeyError, AttributeError, TypeError, IndexError):
            return image

        return image

    def execute(self):
        """
        Start the conversion workflow
        """
        try:
            self.checkdirs()
            _, images = self.check_source_files()
            # self.generate_in_parallel(images=images)
        #pylint: disable=broad-except
        except Exception as error:
            self.logger.error(error)
        finally:
            self.logger.info("Images Generated")


class AsyncConvert(threading.Thread):
    """
    Class to start generation in parallel
    """
