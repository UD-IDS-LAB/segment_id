# Eric Rivas
# January 8, 2020

import cv2; import numpy; import csv; import math; import matplotlib.pyplot as plt
import time

def segmentID(x,y):
    global line_list, dictObj, validSegments, arc_list

    line_list = []
    arc_list = []
    valid_segment = []
    tolerance = 0.1 # accounts for the width of the segments and some car width
    
    # read in line segment data
    with open(r'/home/themainframe/Desktop/rivas-ids-segment-id/lines.csv') as csv_file:
        
        csv_reader = csv.reader(csv_file, delimiter=',')

        for row in csv_reader:
            dictObj = {'segment': row[0], 'direction': row[1], 'length':row[2], 'x': row[3], 'y': row[4]}
            line_list.append(dictObj)            

            if row != 0:
                if dictObj['direction'] == '-X': # horizontal line going right
                    dictObj['xf'] = float(dictObj['x']) + float(dictObj['length'])
                    dictObj['yf'] = float(dictObj['y'])
                    dictObj['x_lower'] = float(dictObj['x']) - tolerance
                    dictObj['x_upper'] = float(dictObj['xf']) + tolerance
                    dictObj['y_lower'] = float(dictObj['y']) - tolerance
                    dictObj['y_upper'] = float(dictObj['y']) + tolerance
                    
                elif dictObj['direction'] == '+X': # horizontal line going left
                    dictObj['xf'] = float(dictObj['x']) - float(dictObj['length'])
                    dictObj['yf'] = float(dictObj['y'])
                    dictObj['x_lower'] = float(dictObj['xf']) - tolerance
                    dictObj['x_upper'] = float(dictObj['x']) + tolerance
                    dictObj['y_lower'] = float(dictObj['y']) - tolerance
                    dictObj['y_upper'] = float(dictObj['y']) + tolerance
                    
                elif dictObj['direction'] == '-Y': # vertical line going down
                    dictObj['yf'] = float(dictObj['y']) + float(dictObj['length'])
                    dictObj['xf'] = float(dictObj['x'])
                    dictObj['x_lower'] = float(dictObj['x']) - tolerance
                    dictObj['x_upper'] = float(dictObj['x']) + tolerance
                    dictObj['y_lower'] = float(dictObj['y']) - tolerance
                    dictObj['y_upper'] = float(dictObj['yf']) + tolerance
                    
                elif dictObj['direction'] == '+Y': # vertical line going up
                    dictObj['yf'] = float(dictObj['y']) - float(dictObj['length'])
                    dictObj['xf'] = float(dictObj['x'])
                    dictObj['x_lower'] = float(dictObj['x']) - tolerance
                    dictObj['x_upper'] = float(dictObj['x']) + tolerance
                    dictObj['y_lower'] = float(dictObj['yf']) - tolerance
                    dictObj['y_upper'] = float(dictObj['y']) + tolerance

    # check if the given position is on a valid line segment(s)    
    i = 1
    while i < len(line_list):
        if mode == 'c':
            if line_list[i]['x_lower'] <= x_grid[x] <= line_list[i]['x_upper'] and line_list[i]['y_lower'] <= y_grid[y] <= line_list[i]['y_upper']:
                valid_segment.append(line_list[i]['segment'])
        else:
            if line_list[i]['x_lower'] <= x <= line_list[i]['x_upper'] and line_list[i]['y_lower'] <= y <= line_list[i]['y_upper']:
                valid_segment.append(line_list[i]['segment'])
        i += 1

    
    # read in arc segment data
    with open(r'/home/themainframe/Desktop/rivas-ids-segment-id/arcs.csv') as csv_file: 
        csv_reader = csv.reader(csv_file, delimiter=',')
        next(csv_reader) # skipping the header line to parse only data
        for row in csv_reader:
            dictObj_arc = {'segment': row[0], 'x': row[1], 'y':row[2], 'radius': row[3], 'angleStart': row[4], 'angleEnd': row[5], 'rotation': row[6]}
            arc_list.append(dictObj_arc)
                  
            if row != 0 and row != 1:
                x_upperbounds = []; x_lowerbounds = []; y_upperbounds = []; y_lowerbounds = [];
                theta_range = numpy.linspace(float(dictObj_arc['angleStart']),float(dictObj_arc['angleEnd']),11)
    
                for theta in theta_range:
                    x_upperbounds.append((float(dictObj_arc['x']) + float(dictObj_arc['radius']) * math.cos(theta)) + tolerance)           
                    x_lowerbounds.append((float(dictObj_arc['x']) + float(dictObj_arc['radius']) * math.cos(theta)) - tolerance)
                    y_upperbounds.append((float(dictObj_arc['y']) + float(dictObj_arc['radius']) * math.sin(theta)) + tolerance)             
                    y_lowerbounds.append((float(dictObj_arc['y']) + float(dictObj_arc['radius']) * math.sin(theta)) - tolerance)

                dictObj_arc['theta_range'] = theta_range
                dictObj_arc['x_upper'] = x_upperbounds; dictObj_arc['x_lower'] = x_lowerbounds;
                dictObj_arc['y_upper'] = y_upperbounds; dictObj_arc['y_lower'] = y_lowerbounds;                      

    # check if the given position is on a valid arc segment(s)    
    i = 1
    while i < len(arc_list):
        idx = 0
        while idx < len(arc_list[i]['x_lower']):
            if mode == 'c':               
                if arc_list[i]['x_lower'][idx] <= x_grid[x] <= arc_list[i]['x_upper'][idx] and arc_list[i]['y_lower'][idx] <= y_grid[y] <= arc_list[i]['y_upper'][idx] and arc_list[i]['segment'] not in valid_segment:
                    valid_segment.append(arc_list[i]['segment'])
            else:
                if arc_list[i]['x_lower'][idx] <= x <= arc_list[i]['x_upper'][idx] and arc_list[i]['y_lower'][idx] <= y <= arc_list[i]['y_upper'][idx] and arc_list[i]['segment'] not in valid_segment:
                    valid_segment.append(arc_list[i]['segment'])
            idx += 1
        i += 1

    return valid_segment


def exportData(): # call in command window to export data. will not overwrite existing csv files with same name.
    with open('line_clickbox.csv', mode='w', newline='') as line_clickbox:
        line_clickbox = csv.writer(line_clickbox, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        line_clickbox.writerow(['Index', 'centerX', 'centerY', 'Width', 'Height'])
        
        i = 1
        while i < len(line_list):
            index = line_list[i]['segment']
            centerX = (line_list[i]['x_upper']+line_list[i]['x_lower']) / 2
            centerY = (line_list[i]['y_upper']+line_list[i]['y_lower']) / 2
            width = abs(line_list[i]['x_upper']-line_list[i]['x_lower'])
            height = abs(line_list[i]['y_upper']-line_list[i]['y_lower']) 
            line_clickbox.writerow([index, centerX, centerY, width, height])
            i += 1
            
    with open('arc_clickbox.csv', mode='w', newline='') as arc_clickbox:
        arc_clickbox = csv.writer(arc_clickbox, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        arc_clickbox.writerow(['Index', 'theta', 'x_upper', 'x_lower', 'y_upper', 'y_lower'])
        
        i = 1
        while i < len(arc_list):
            index = arc_list[i]['segment']
            idx = 0
            while idx < len(arc_list[i]['theta_range']):
                theta = arc_list[i]['theta_range'][idx]
                x_upper = arc_list[i]['x_upper'][idx]
                x_lower = arc_list[i]['x_lower'][idx]
                y_upper = arc_list[i]['x_upper'][idx]
                y_lower = arc_list[i]['y_lower'][idx]
                arc_clickbox.writerow([index, theta, x_upper, x_lower, y_upper, y_lower])
                idx += 1
            i += 1
        

def onMouse(event, x, y, flags, param):
   if event == cv2.EVENT_LBUTTONDOWN:       
       print('\nPixel Coord:', x,y)      
       print('Scaled Coord:', round(x_grid[x],3),round(y_grid[y],3)) # converts pixel coord to meter scale
       print(segmentID(x,y)) 
       posList.append((x, y)) # storing click data. use for mapping trajectories in future with GUI ?


def main():
    global posList, img, path, x_grid, y_grid, mode
    path = r'/home/themainframe/Desktop/rivas-ids-segment-id/citymap.jpg'    
    img = cv2.imread(path)
    mode = str.lower(raw_input('Manual Input (m) or Click Input (c): '))

    x_grid = numpy.linspace(3.048, -3.048, img.shape[1])
    y_grid = numpy.linspace(-4.572, 1.524, img.shape[0])
    x_grid = list(x_grid)
   
    if mode == 'c':    
        posList = [] # stores mouse click coordinates      
#        cv2.setMouseCallback('WindowName', onMouse)
        posNp = numpy.array(posList)     # convert to numpy for other usages
        cv2.namedWindow('image',cv2.WINDOW_NORMAL)
        cv2.resizeWindow('image', img.shape[0],img.shape[1])
        cv2.imshow('image', img)
        cv2.setMouseCallback('image', onMouse)
        cv2.waitKey(0)

    elif mode == 'm':
        x_manual = float(input('x: '))
        y_manual = float(input('y: '))
        print(segmentID(x_manual, y_manual)) # random input needs to take pixel coord. find way to convert.

    else:
        print('invalid input\n')
        main()


main()
