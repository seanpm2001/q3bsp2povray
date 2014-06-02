#!/usr/bin/env python3

__all__ = (
    'main',
    'BspScene',
)

from pprint import pprint
import argparse
import pprint
import sys

import povray.sdl
import q3.bsp
import q3.fs


def warn(s):
    sys.stderr.write("Warning: {}\n".format(s))


class _BspCamera():
    VIEW_CLASS = 'info_player_intermission'

    def _get_entity(self, field, val):
        ents = [ent for ent in self._bsp.entities
                if field in ent and ent[field] == val]
        assert len(ents) == 1
        return ents[0]

    def __init__(self, bsp):
        self._bsp = bsp

        # Quake 3 has the "z" coordinates being up/down.
        self.up = "z"

        # Calculate the location/direction.
        view_ent = self._get_entity('classname', self.VIEW_CLASS)
        target_ent = self._get_entity('targetname', view_ent["target"])

        self.location = view_ent["origin"]
        self.direction = tuple(a - b for a, b in zip(target_ent["origin"],
                                                     view_ent["origin"]))

        # Print a comment making it clear which entities were used for the
        # camera.
        self.comment = "view_ent:\n"
        self.comment += pprint.pformat(view_ent, 4)
        self.comment += "\n\n"
        self.comment += "target_ent:\n"
        self.comment += pprint.pformat(target_ent, 4)
        self.comment += "\n"

class _BspTri():
    def __init__(self, *verts, comment=""):
        assert len(verts) == 3
        self._verts = verts
        self.comment = comment

    def __iter__(self):
        return iter(self._verts)

    def __len__(self):
        return len(self._verts)

class BspScene():
    """
    An SDL scene, constructed from a `q3.bsp.Bsp` instance.

    This satifies the definition of a scene, described in `povray.sdl`.

    """
    @property
    def tris(self):
        """
        Generate triangles by using a polygon fan approach on each face.

        """
        for face_idx, face in enumerate(self._bsp.faces):
            if len(face.verts) < 3:
                warn("{} (idx = {}) has < 3 "
                    "verts".format(face, face_idx))
                continue

            first_vert = face.verts[0]
            for vert_idx in range(2, len(face.verts)):
                comment = "Face = {}\n".format(face)
                comment += "Face idx {} Tri idx {}\n".format(
                               face_idx, vert_idx)
                yield _BspTri(
                       first_vert,
                       face.verts[vert_idx - 1],
                       face.verts[vert_idx],
                       comment=comment)

    @property
    def camera(self):
        return _BspCamera(self._bsp)


    def __init__(self, bsp):
        self._bsp = bsp


def _parse_args(in_args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseq3", "-b",
            help="Directory containing pk3 files", required=True)
    parser.add_argument("--map", "-m", help="The map to view", required=True)
    parser.add_argument("--output-file", "-o", help="SDL output file")

    return parser.parse_args(in_args)


def main(argv):
    args = _parse_args(argv)

    sdl_file = open(args.output_file, "w") if args.output_file else sys.stdout

    fs = q3.fs.FileSystem.from_dir(args.baseq3)

    with fs.open("maps/{}.bsp".format(args.map)) as bsp_file:
        bsp = q3.bsp.Bsp(bsp_file)
        scene = BspScene(bsp)
        povray.sdl.write(sdl_file, scene)

if __name__ == "__main__":
    main(sys.argv[1:])