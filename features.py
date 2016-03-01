import subprocess
import numpy as np

def imodinfo_e(fname, iObj, ncont):
    """
    Runs imodinfo with the -e flag for a given object of the input model file.
    This will output metrics related to the ellipticity of all contours in the
    object, including: (1) the contour's semi-major and semi-minor axes, (2)
    the eccentricity, and (3) the long angle. These are stored to an array,
    with one line for each contour.

    Inputs
    ======
    fname - Filename of the IMOD model file to load.
    iObj  - Object number to analyze of the file specified by fname.
    ncont - Number of contours in the object

    Returns
    =======
    M - A numpy array of size (ncont x 5), in which the metrics of each contour
        are stored to their corresponding numbered lines. The metrics stored
        are: (1) Semi-major axis length, (2) semi-minor axis length, (3) the
        ratio of semi-major to semi-minor, (4) eccentricity, and (5) long angle.
    """

    # Run the command and get its output
    cmd = "imodinfo -e -o {0} {1}".format(iObj + 1, fname)
    proc = subprocess.Popen(cmd.split(), stdout = subprocess.PIPE)

    # Initialize an empty array to store metrics in
    M = np.zeros([ncont, 5])

    data_switch = 0
    C = 1
    for line in proc.stdout:
        # Initialize data storing after the imodinfo header line
        if not data_switch and "semi-major" in line:
            data_switch = 1
        elif data_switch and C <= ncont:
            line = line.split()
            # If C is less than the # of contours and the line contains
            # 'Mean', this means some contours were not computed properly.
            # Not sure why this happens, but when it does, they are 
            # completely skipped in the imodinfo output. When this occurs,
            # store NaNs to the array. Future functions will interpret these
            # NaNs as belonging toskipped contours.
            if str(line[0]) == 'Mean':
                delta = ncont - C + 1
                for i in range(delta):
                    M[C-1,:] = np.nan
                    C+=1
                continue
            # Likewise, if the contour number of the current line is not the
            # same as C, a contour has been skipped. Store a line of NaNs.
            if C != int(line[0]):
                delta = int(line[0]) - C
                for i in range(delta):
                    M[C-1,:] = np.nan
                    C+=1
            # Otherwise, store the correct data to the current line of the 
            # array M. Data stored are: (1) Semi-major, (2) Semi-minor, (3)
            # Ratio of semi-major to semi-minor, (4) eccentricity, and (5)
            # long angle.
            if C <= ncont:
                M[C-1,0] = float(line[4])
                M[C-1,1] = float(line[5])
                M[C-1,2] = M[C-1,0] / M[C-1,1]
                M[C-1,3] = float(line[6])
                M[C-1,4] = float(line[7])
                C+=1
    return M

def imodinfo_v(fname, iObj, ncont):
    """
    Runs imodinfo with the -v flag for a given object of the input model file.
    This will output a host of metrics for every contour in the object,
    including: (1) The number of points, (2) the closed length, (3) the open
    length, (4) the contour enclosed area, (5) the contour's center of mass,
    (6) the contour's circularity, (7) orientation angle, (8) ellipticity, (9)
    length, (10) width, (11) aspect ratio, (12) mesh volume, and (13) mesh
    surface area. Items 1-11 are stored to a numpy array, in which each line 
    corresponds to the metrics for its numbered contour.

    Inputs
    ======
    fname - Filename of the IMOD model file to load.
    iObj  - Object number to analyze of the file specified by fname.
    ncont - Number of contours in the object

    Returns
    =======
    M      - A numpy array of size (ncont x 13), in which the metrics of each
             contour are stored to their corresponding numbered lines.
    volume - Mesh volume of the entire object, given in microns cubed.
    sa     - Mesh surface area of the entire object, given in microns cubed.
    """

    # Run the command and get its output
    cmd = "imodinfo -v -o {0} {1}".format(iObj + 1, fname)
    proc = subprocess.Popen(cmd.split(), stdout = subprocess.PIPE)

    # Initialize an empty array to store metrics in
    M = np.zeros([ncont, 13])

    # Loop over all contours, and extract and store their metrics. Volume
    # and surface area are stored to separate variables, as they are given
    # for the whole object, rather than individual contours.
    C = -1
    for line in proc.stdout:
        if "CONTOUR" in line:
            C+=1
            M[C,0] = line.split()[2] #N points
        elif "Closed/Open length" in line:
            M[C,1] = line.split()[3] #Closed length
            M[C,2] = line.split()[5] #Open length
        elif "Enclosed Area" in line:
            M[C,3] = line.split()[3] #Area
        elif "Center of Mass" in line:
            M[C,4] = line.split()[4][1:-1] #Centroid X
            M[C,5] = line.split()[5][0:-1] #Centroid Y
            M[C,6] = line.split()[6][0:-1] #Centroid Z
        elif "Circle" in line:
            M[C,7] = line.split()[2] #Circle
        elif "Orientation" in line:
            M[C,8] = line.split()[2] #Orientation
        elif "Ellipse" in line:
            M[C,9] = line.split()[2] #Ellipse
        elif "Length X Width" in line:
            M[C,10] = line.split()[4] #Length
            M[C,11] = line.split()[6] #Width
        elif "Aspect Ratio" in line:
            M[C,12] = line.split()[3] #Aspect Ratio
        elif "Total volume inside mesh" in line:
            volume = float(line.split()[5]) / (1000 ** 3) #Volume
        elif "Total mesh surface area" in line:
            sa = float(line.split()[5]) / (1000 ** 2) #Surface Area
    return M, volume, sa