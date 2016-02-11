from __future__ import division
from .utils import is_string

def ImodExport(tag, input, **kwargs):
    iObject = kwargs.get('object', 0)
    is_string(tag, 'Export tag')
    objType = type(input).__name__
    mats = []
    scale = [1, 1, 1]
    trans = [0, 0, 0]
    if objType == 'ImodModel':
        if not iObject:
            raise ValueError('Must specify object number with object kwarg.')
        iObject-=1
        mesh = get_mesh(input, iObject)
        name = input.Objects[iObject].name
        mats.append(input.Objects[iObject].ambient / 255)
        mats.append(input.Objects[iObject].diffuse / 255)
        mats.append(input.Objects[iObject].specular / 255)
        mats.append(input.Objects[iObject].shininess / 255)
        mats.append(input.Objects[iObject].transparency)
        if input.minx_set:
            scale = input.minx_cscale
            trans = input.minx_ctrans
    else:
        raise ValueError('input is not a valid class type.')

    if tag.lower() == 'vrml' or tag.lower() == 'wrl':
        export_vrml2(mesh, iObject, name, mats, scale, trans)

def get_mesh(imodModel, iObject):
    nObjects = imodModel.nObjects
    if iObject > nObjects:
        raise ValueError('Value specified by object kwarg exceeds nObjects.')
    nMeshes = imodModel.Objects[iObject].nMeshes
    if nMeshes > 1:
        raise ValueError('Object {0} contains > 1 mesh.'.format(iObject+1))
    mesh = imodModel.Objects[iObject].Meshes[0]
    return mesh

def export_vrml2(mesh, iObject, name, mats, scale, trans):
    iObject+=1
    zscale = scale[2] / scale[0]
    nameStr = 'obj{0}'.format(iObject)
    if name:
        for x in name.split():
            nameStr = nameStr + '_' + x 
    fid = open('pyimod.wrl', 'w+')

    # Write VRML 2.0 header data
    fid.write('#VRML V2.0 utf8\n')
    fid.write('#Generated by pyimod\n\n')
    fid.write('DEF imod_model Transform {\n')
    fid.write('  children [\n\n')
    fid.write('#MATERIAL FOR OBJECT {0}:\n'.format(iObject))
    fid.write('Shape {\n')
    fid.write('  appearance DEF {0} Appearance {{\n'.format('MAT_' + nameStr))
    fid.write('    material Material {\n')
    fid.write('      ambientIntensity {0}\n'.format(mats[0]))
    fid.write('      diffuseColor {0} {0} {0}\n'.format(mats[1]))
    fid.write('      specularColor {0} {0} {0}\n'.format(mats[2]))
    fid.write('      emissiveColor 0 0 0\n')
    fid.write('      shininess {0}\n'.format(mats[3]))
    fid.write('      transparency {0}\n'.format(mats[4]))
    fid.write('    }\n')
    fid.write('  }\n')
    fid.write('}\n\n')
    fid.write('#DATA FOR OBJECT {0}:\n'.format(iObject)) 
    fid.write('DEF {0} Transform {{\n'.format(nameStr))
    fid.write('  children [\n')
    fid.write('    Shape {   #MESH\n')
    fid.write('      appearance USE {0}\n'.format('MAT_' + nameStr))
    fid.write('      geometry DEF {0} IndexedFaceSet {{\n'.format(nameStr))
    fid.write('        ccw FALSE\n')
    fid.write('        solid FALSE\n')
    fid.write('        creaseAngle 1.56207\n')
    fid.write('        coord Coordinate {\n')
    fid.write('          point [   # list of all points in mesh\n') 

    # Write VRML 2.0 mesh vertex data
    C = 0
    nvertlist = len(mesh.vertices)
    while C < nvertlist:
        x, y, z = [mesh.vertices[C+x] for x in range(3)]
        x = x * scale[0] + trans[0]
        y = y * scale[1] + trans[1]
        z = z * scale[2]/zscale + trans[2]
        x = '{0:.1f}'.format(x) if x % 1 else int(x)
        y = '{0:.1f}'.format(y) if y % 1 else int(y)
        z = '{0:.1f}'.format(z) if z % 1 else int(z)
        fid.write('            {0} {1} {2},\n'.format(x, y, z))
        C+=6 
    fid.write('          ]\n')
    fid.write('        }\n')    

    # Write VRML 2.0 mesh index data
    C = 0
    nindexlist = len(mesh.indices)
    fid.write('        coordIndex [   # connect triangles\n')
    while C < nindexlist:
        if mesh.indices[C] < 0:
            C+=1
            continue
        else:
            fid.write('          {0},{1},{2},-1,\n'.format(
                int(mesh.indices[C+2] / 2),
                int(mesh.indices[C+1] / 2),
                int(mesh.indices[C] / 2)))    
            C+=3
    fid.write('        ]\n')
    fid.write('      }\n')
    fid.write('    }\n')
    fid.write('  ]\n')
    fid.write('}\n\n') 
    fid.write('  ]\n')
    fid.write('}\n')
    fid.close()
 
