# -*- Mode: python; tab-width: 4; indent-tabs-mode:nil; coding:utf-8 -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
#
# MDAnalysis --- https://www.mdanalysis.org
# Copyright (c) 2006-2017 The MDAnalysis Development Team and contributors
# (see the file AUTHORS for the full list of names)
#
# Released under the GNU Public Licence, v2 or any higher version
#
# Please cite your use of MDAnalysis in published work:
#
# R. J. Gowers, M. Linke, J. Barnoud, T. J. E. Reddy, M. N. Melo, S. L. Seyler,
# D. L. Dotson, J. Domanski, S. Buchoux, I. M. Kenney, and O. Beckstein.
# MDAnalysis: A Python package for the rapid analysis of molecular dynamics
# simulations. In S. Benthall and S. Rostrup editors, Proceedings of the 15th
# Python in Science Conference, pages 102-109, Austin, TX, 2016. SciPy.
#
# N. Michaud-Agrawal, E. J. Denning, T. B. Woolf, and O. Beckstein.
# MDAnalysis: A Toolkit for the Analysis of Molecular Dynamics Simulations.
# J. Comput. Chem. 32 (2011), 2319--2327, doi:10.1002/jcc.21787
#

"""\
Trajectory translation --- :mod:`MDAnalysis.transformations.translate`
=====================================================================

Translate the coordinates of a given trajectory by a given vector.
The vector can either be user defined, using the function `translate`
or defined by centering an AtomGroup in the unit cell using the function
`center_in_box`
    
"""
from __future__ import absolute_import, division

import numpy as np

from ..lib.mdamath import triclinic_vectors
from ..core.groups import AtomGroup

def translate(vector):
    """
    Translates the coordinates of a given :class:`~MDAnalysis.coordinates.base.Timestep`
    instance by a given vector.
    
    Example
    -------
        ts = MDAnalysis.transformations.translate([1,2,3])(ts)    
    
    Parameters
    ----------
    vector: list
        coordinates of the vector to which the coordinates will be translated
        
    Returns
    -------
    :class:`~MDAnalysis.coordinates.base.Timestep` object
    
    """       
    def wrapped(ts):
        if len(vector)>2:
            v = np.float32(vector)
            ts.positions += v
        else:
            raise ValueError("{} vector is too short".format(vector))
        
        return ts
    
    return wrapped

def center_in_box(ag, center='geometry', point=None, pbc=None):
    """
    Translates the coordinates of a given :class:`~MDAnalysis.coordinates.base.Timestep`
    instance so that the center of geometry/mass of the given :class:`~MDAnalysis.core.groups.AtomGroup`
    is centered on the unit cell. The unit cell dimensions are taken from the input Timestep object or
    can be defined using the `box` argument.
    
    Example
    -------
    
    .. code-block:: python
    
        ag = u.residues[1].atoms
        ts = MDAnalysis.transformations.center(ag,center='mass')(ts)
    
    Parameters
    ----------
    ag: AtomGroup
        atom group to be centered on the unit cell.
    center: str, optional
        used to choose the method of centering on the given atom group. Can be 'geometry'
        or 'mass'
    point: list, optional
        overrides the unit cell center - the coordinates of the Timestep are translated so
        that the center of mass/geometry of the given AtomGroup is aligned to this position
        instead. Defined as a list of size 3. Example: [1, 2, 3]
    pbc: bool or None, optional
        If True, all the atoms from the given AtomGroup will be moved to the unit cell
        before calculating the center of mass or geometry
    
    Returns
    -------
    :class:`~MDAnalysis.coordinates.base.Timestep` object
    """
    
    pbc_arg = pbc
    try:
        if center == 'geometry':
            ag_center = ag.center_of_geometry(pbc=pbc_arg)
        elif center == 'mass':
            ag_center = ag.center_of_mass(pbc=pbc_arg)
        else:
            raise ValueError('{} is not a valid argument for center'.format(center))
    except AttributeError:
        if center == 'mass':
            raise AttributeError('{} is not an AtomGroup object with masses'.format(ag))
        else:
            raise ValueError('{} is not an AtomGroup object'.format(ag))
    
    def wrapped(ts):
        if point:
            if len(point)==3:
                boxcenter = np.float32(point)
            else:
                raise ValueError('{} is not a valid point'.format(point))
        else:
            boxcenter = np.sum(ts.triclinic_dimensions, axis=0) / 2
        vector = boxcenter - ag_center
        ts.positions += vector
        
        return ts
    
    return wrapped
        
            