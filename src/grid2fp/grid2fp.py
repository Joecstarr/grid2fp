"""The grid2fp file.

The class takes a grid diagram to a picture of the front project for a
Legendrian knot.

"""
import drawsvg as draw
import math
import csv
from . import grid_segment


class grid2fp:
    """The grid2fp class."""

    def __init__(self, csv_file=None, diagram=None, eccentricity=0.9) -> None:
        """Init for the grid2fp object.

        Parameters
        ----------
        csv_file : str, optional
            The location of grid diagram as csv, by default None
        diagram : _type_, optional
            A grid diagram, by default None
        eccentricity : float, optional
            How far away to place the
            Bézier controls, by default 0.9
        """
        self.diagram = []
        if csv_file:
            with open(csv_file) as csvfile:
                reader = csv.reader(csvfile, delimiter=" ", quotechar="|")
                for row in reader:
                    self.diagram.append(row)

        if diagram:
            self.diagram = diagram

        self.eccentricity = eccentricity
        self.__get_segments(diagram)

    def __rotate(self, x, y):
        """Do a 45 degree rotation of the point.

        Parameters
        ----------
        x : int
            the x coord
        y : int
            the y coord

        Returns
        -------
        tuple
            rotated cord as tuple
        """
        r = math.sqrt(2) / 2
        return (x * r - y * r, x * r + y * r)

    def __get_segments(self):
        """Parse the grid for segments."""
        self.segments = []
        self.segments.extend(self.__get_segments_horizontal())
        self.segments.extend(self.__get_segments_vertical())
        # Get horizontal

    def __get_segments_horizontal(self):
        """Parse the grid for horizontal segments.

        Returns
        -------
        grid_segment
            The segment.
        """
        segments = []
        for i, row in enumerate(self.diagram):
            seg = None
            for j, c in enumerate(row):
                if c != "":
                    if seg is None:
                        seg = grid_segment()
                    if c == "x":
                        seg.sink = self.__rotate(i, j)
                    if c == "o":
                        seg.source = self.__rotate(i, j)
            if seg is not None:
                segments.append(seg)
        return segments

    def __get_segments_vertical(self):
        """Parse the grid for vertical segments.

        Returns
        -------
        grid_segment
            The segment.
        """
        segments = []
        # Get vertical
        for j, c in enumerate(self.diagram[0]):
            seg = None
            for i, row in enumerate(self.diagram):
                if row[j] != "":
                    if seg is None:
                        seg = grid_segment()
                    if row[j] == "x":
                        seg.source = self.__rotate(i, j)
                    if row[j] == "o":
                        seg.sink = self.__rotate(i, j)
            if seg is not None:
                segments.append(seg)
        return segments

    def __draw_segment(self, step):
        """Draws a segment of the front projection as a Bézier curve.

        Parameters
        ----------
        step : grid_segment
            The segment to draw.

        Returns
        -------
        Path
            The svg path segment.
        """
        p = draw.Path()
        p.M(step.source[0], step.source[1])
        delta_x = step.sink[0] - step.source[0]
        x_ctr1 = step.source[0] + (self.eccentricity * delta_x)
        x_ctr2 = step.sink[0] - (self.eccentricity * delta_x)
        y_ctr1 = step.source[1]
        y_ctr2 = step.sink[1]
        p.C(x_ctr1, y_ctr1, x_ctr2, y_ctr2, step.sink[0], step.sink[1])
        return p

    def draw(self, file, pixel_scale=2):
        """Draws the front projection of the given grid as an SVG.

        Parameters
        ----------
        file : str
            The output file
        pixel_scale : int, optional
            The scaling for pixel features, by default 2
        """
        d = draw.Drawing(
            len(self.diagram[0]),
            math.sqrt(2) * len(self.diagram[0]),
            origin=(0, 0),
            id_prefix="d",
        )
        g = draw.Group(
            stroke_width=0.1,
            stroke="black",
            fill="none",
            transform=f"translate({len(self.diagram[0])/2},0.1)",
        )
        for step in self.segments:
            p = self.__draw_segment(step)
            g.append(p)
        d.append(g)

        d.set_pixel_scale(pixel_scale)
        d.save_svg(file)
