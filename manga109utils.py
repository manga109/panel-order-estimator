from PIL import Image
import manga109api
import pathlib
import os

class BoundingBox(object):
    def __init__(self, xmin=None, ymin=None, xmax=None, ymax=None,
    panels=None,
    bbtype=None,
    id_=""):
        self.dict = {
            "@xmin": xmin,
            "@ymin": ymin,
            "@xmax": xmax,
            "@ymax": ymax,
            "@id": id_,
        }
        if panels is None:
            self.panels = [self]
        else:
            self.panels = panels
        self.bbtype = bbtype

    def init_dict(self, d):
        self.dict = d
        self.dict["@xmin"] = float(self.xmin)
        self.dict["@ymin"] = float(self.ymin)
        self.dict["@xmax"] = float(self.xmax)
        self.dict["@ymax"] = float(self.ymax)
        return self

    def __getitem__(self, index):
        return self.dict[index]

    @property
    def xmin(self):
        return self.dict["@xmin"]

    @property
    def xmax(self):
        return self.dict["@xmax"]

    @property
    def ymin(self):
        return self.dict["@ymin"]

    @property
    def ymax(self):
        return self.dict["@ymax"]

    @property
    def width(self):
        return self.xmax - self.xmin

    @property
    def height(self):
        return self.ymax - self.ymin

    @property
    def text(self):
        return self.dict["#text"]

    @property
    def id(self):
        return self.dict["@id"]

    @property
    def list(self):
        return [self.xmin, self.ymin, self.xmax, self.ymax]

    @property
    def is_null(self):
        return self.xmin is None or self.ymin is None or self.xmax is None or self.ymax is None

    @property
    def area(self):
        if self.xmax is None or self.xmin is None or self.ymax is None or self.ymin is None:
            return 0
        return (self.xmax - self.xmin) * (self.ymax - self.ymin)

    @property
    def base_panels(self):
        return len(self.panels)


    def __getitem__(self, item):
        return self.dict[item]

    def __add__(self, a):
        assert issubclass(type(a), BoundingBox)
        if a.is_null:
            return self
        elif self.is_null:
            return a
        return BoundingBox(xmin=min(self.xmin, a.xmin),
                           ymin=min(self.ymin, a.ymin),
                           xmax=max(self.xmax, a.xmax),
                           ymax=max(self.ymax, a.ymax),
                           panels=self.panels + a.panels)

    def __mul__(self, a):
        assert issubclass(type(a), BoundingBox)
        bb = BoundingBox(xmin=max(self.xmin, a.xmin),
                         ymin=max(self.ymin, a.ymin),
                         xmax=min(self.xmax, a.xmax),
                         ymax=min(self.ymax, a.ymax),
                         panels=self.panels + a.panels)
        if bb.xmin > bb.xmax or bb.ymin > bb.ymax:
            return BoundingBox()
        else:
            return bb

    def __repr__(self):
        return "<BoundingBox({},{}) {},{},{},{},{}>".format(self.bbtype, self.id, *self.list, self.base_panels)


class Page(object):
    labels = ["frame", "text", "face", "body"]

    def __init__(self, parent, page_index):
        self.parent = parent
        self.page_index = page_index

        pagewidth = self.parent.annotations["page"][self.page_index]["@width"]
        pageheight = self.parent.annotations["page"][self.page_index]["@height"]
        self.pagedims = (pagewidth, pageheight)

    def get_image(self):
        img = Image.open(self.parent.get_image_path(self.page_index))
        return img

    def get_bbs(self):
        bb_dict = dict([(a,[BoundingBox(bbtype=a).init_dict(d) for d in self.parent.annotations["page"][self.page_index][a]]) for a in self.labels])
        return bb_dict


class Book(object):
    def __init__(self, title, loader=None, manga109_root_dir="./dataset/Manga109_released_2021_02_28"):
        self.manga109_root_dir = manga109_root_dir
        self.title = title
        if loader is None:
            self.loader = manga109api.Parser(root_dir=manga109_root_dir)
        else:
            self.loader = loader
        self.annotations = self.loader.get_annotation(book=title)

    def get_image_path(self, i_page):
        bookimgpath = pathlib.Path(
            self.manga109_root_dir) / "images" / self.title
        return str(bookimgpath / list(sorted(os.listdir(str(bookimgpath))))[i_page])

    def get_page_iter(self, max_pages=None):
        for page_index in range(self.n_pages):
            if max_pages is not None and page_index >= max_pages - 1:
                break
            yield Page(self, page_index)

    @property
    def n_pages(self):
        return len(self.annotations["page"])

class Manga109Dataset(object):
    def __init__(self, manga109_root_dir="./dataset/Manga109_released_2021_02_28"):
        self.manga109_root_dir = manga109_root_dir
        self.loader = manga109api.Parser(root_dir=manga109_root_dir)

    @property
    def books(self):
        return self.loader.books

    def get_book_iter(self):
        for title in self.books:
            yield Book(title, loader=self.loader, manga109_root_dir=self.manga109_root_dir)

    def get_book(self, title):
        return Book(title,
                    loader=self.loader,
                    manga109_root_dir=self.manga109_root_dir)
