# Desenvolvido por: Luciano Soares
# Displina: Computação Gráfica
# Data: 28 de Agosto de 2020

import argparse

# X3D
import x3d

# Interface
import interface

# GPU
import gpu

#newimports
import math

def polypoint2D(point, color):
    """ Função usada para renderizar Polypoint2D. """
    #gpu.GPU.set_pixel(3, 1, 255, 0, 0) # altera um pixel da imagem
    #point is a list (x1,y1,x2,y2,x3,y2)
    #color = (r,g,b. de 0 a 1) (tem q converter a 255)
    # cuidado com as cores, o X3D especifica de (0,1) e o Framebuffer de (0,255)

    bitcolor = []
    for i in color:
        bitcolor.append(int(i * 255))

    i = 0
    while i < (len(point)):
        x_round = math.floor(point[i])
        y_round = math.floor(point[i+1])
        if x_round >= width:
            x_round = width-1
        if y_round >= height:
            y_round = height-1
        gpu.GPU.set_pixel(x_round, y_round, bitcolor[0], bitcolor[1], bitcolor[2]) # altera um pixel da imagem
        i+=2

def polyline2D(lineSegments, color):
    """ Função usada para renderizar Polyline2D. """
    #x = gpu.GPU.width//2
    #y = gpu.GPU.height//2
    #gpu.GPU.set_pixel(x, y, 255, 0, 0) # altera um pixel da imagem
    print(lineSegments)
    
    bitcolor = []
    for i in color:
        bitcolor.append(int(i * 255))
    
    #x = u
    #y = v
    #getting values for readbility
    if(lineSegments[0] < lineSegments[2]):
        v1 = lineSegments[1]
        v2 = lineSegments[3]
        u1 = lineSegments[0]
        u2 = lineSegments[2]
    else:
        v2 = lineSegments[1]
        v1 = lineSegments[3]
        u2 = lineSegments[0]
        u1 = lineSegments[2]

    #calc angular coeficient
    if(u2 - u1 == 0):
        s = math.inf
    else:
        s = (v2-v1) / (u2-u1)
    #print(s)
    #calc angular coef and set u and v
    u = u1
    v = v1

    if(math.fabs(s) <= 1):
        while(u <= u2):
            gpu.GPU.set_pixel(math.floor(u), math.floor(v), bitcolor[0], bitcolor[1], bitcolor[2])
            v += s
            u += 1

    else: #if line is vertical, change the logic a bit
        s = 1/s
        #required in some cases
        if(v2 < v1):
            u = u2
            v = v2
            while(v <= v1):
                gpu.GPU.set_pixel(math.floor(u), math.floor(v), bitcolor[0], bitcolor[1], bitcolor[2])
                v += 1
                u += s
        else:
            while(v <= v2):
                gpu.GPU.set_pixel(math.floor(u), math.floor(v), bitcolor[0], bitcolor[1], bitcolor[2])
                v += 1
                u += s

#funcs for triangle:
def dot(a,b):
    #a and b are 2sized float lists
    return a[0]*b[0] + a[1]*b[1]

def get_angle(vec1, vec2): 
    #both vectors have a point in common (the second point)
    a = [vec1[0],vec1[1]]
    b = [vec1[2],vec1[3]]
    c = [vec2[0],vec2[1]]

    #line adapted from: https://medium.com/@manivannan_data/find-the-angle-between-three-points-from-2d-using-python-348c513e2cd
    ang = math.degrees(math.atan2(c[1]-b[1], c[0]-b[0]) - math.atan2(a[1]-b[1], a[0]-b[0]))
    ret = ang + 360 if ang < 0 else ang

    if ret > 180:
        ret = 360 - ret
    return ret

def check_point(vertices, point):
    #if the sum of the angle of the vectors between the point and each vertices is 360, the point is inside
    vectors = []
    '''
    for i in range(0,len(vertices),2):
        vectors.append(vertices[i] - point[0])
        vectors.append(vertices[i+1] - point[1])
    '''
    for i in range(0,len(vertices),2):
        v = [vertices[i],vertices[i+1],point[0],point[1]]
        vectors.append(v)
    #print(vectors)
    #DEBUG
    #polyline2D(vectors[0],[1,1,1])
    #print(get_angle(vectors[0],vectors[1]))
    angles = []
    angles.append(get_angle(vectors[0],vectors[1]))
    angles.append(get_angle(vectors[1],vectors[2]))
    angles.append(get_angle(vectors[2],vectors[0]))
    
    #config

    THRESHOLD = 0.02 #deegres. This set the amount of error that still confirms a point is inside a triangle

    anglesum = sum(angles)

    return (anglesum < (360 + THRESHOLD) and anglesum > (360 - THRESHOLD))

def draw_pixel(vertices, color, pixel):

    #DEBUG: White background (sets the pixel to white before checking it, to see witch pixels are being rendered and debuging)
    '''
    if(pixel[0] > LARGURA) or (pixel[1] > ALTURA):
        return False
    gpu.GPU.set_pixel(pixel[0], pixel[1], 255, 255, 255)
    '''
    intensity = 0 #this is returnet to know how many 

    #Eh um antialising! Eh uma otimizacao em GPU! NAO!!! Eh o SUPER SAMPLING!!!
    SSP = [
            [pixel[0] + 0.3, pixel[1] + 0.3],
            [pixel[0] + 0.7, pixel[1] + 0.3],
            [pixel[0] + 0.3, pixel[1] + 0.7],
            [pixel[0] + 0.7, pixel[1] + 0.7]
        ]

    for i in SSP:
        if check_point(vertices,i):
            intensity += 1 / len(SSP)
    
    bitcolor = []
    for i in color:
        bitcolor.append(int((i) * 255))

    if(intensity == 0):
        return False
    
    #if triangle is above another rendered object
    old_color = gpu.GPU.get_pixel(pixel[0],pixel[1])

    #OLD Linear transparency calc.
    #r = old_color[0] * (1 - intensity) + bitcolor[0] * intensity
    #g = old_color[1] * (1 - intensity) + bitcolor[1] * intensity
    #b = old_color[2] * (1 - intensity) + bitcolor[2] * intensity

    #quadratic normalized transparency
    r = ( (old_color[0]**2) * (1 - intensity) + (bitcolor[0]**2) * intensity )**0.5
    g = ( (old_color[1]**2) * (1 - intensity) + (bitcolor[1]**2) * intensity )**0.5
    b = ( (old_color[2]**2) * (1 - intensity) + (bitcolor[2]**2) * intensity )**0.5

    #unfortunally the class GPU does not support an alpha channel Dx

    gpu.GPU.set_pixel(pixel[0], pixel[1], r, g, b)

    return True


def triangleSet2D(vertices, color):
    """ Função usada para renderizar TriangleSet2D. """
    #gpu.GPU.set_pixel(24, 8, 255, 255, 0) # altera um pixel da imagem
    print(vertices)
    #print(check_point(vertices,[10,10]))

    #check every pixel
    '''
    for i in range(30):
        for j in range(20):
            draw_pixel(vertices,color,[i,j])
    '''

    #pseudo zig-zag
    #start on highest vertice
    #go right until end of triangle
    #go left until end of triangle
    #go down one
    #search triangle
    #repeat until below lowest Y

    #get highest vertice (high is a lower Y value)
    highest = ALTURA
    lowest = 0
    high_id = 0

    for i in range(3):
        y = vertices[(i*2) + 1]
        if(y < highest):
            highest = y
            high_id = i
        if (y > lowest):
            lowest = y
    #start on it:

    pixel = [math.floor(vertices[high_id*2]), math.floor(vertices[high_id*2 + 1])]
    lowest = math.floor(lowest)
    print("pixel mais alto: " ,pixel)
    print("y mais baixo: " , lowest)

    #start loop:
    origin = pixel[0]
    line = pixel[1]
    delta = 0
    lost = False
    full = False
    state = "down" #right, left, down, search

    render_count = 0 
    #DEBUG
    speed = 10
    while line < lowest:
        #THERE IS NO SWITCH CASE IN PYTHON!!! (sad music starts playing)
        drew = draw_pixel(vertices,color,[origin + delta, line])
        render_count += 1
        #If you want to see this algo running, uncomment this speed if and the first DEBUG line on Draw_pixel (white bg)
        '''
        if speed == 0:
            interface.Interface(LARGURA, ALTURA, image_file).preview(gpu.GPU._frame_buffer)
            speed = 10
        else:
            speed -= 1
        '''
        if state == "down":
            if drew:
                state = "right"
                delta = 1
            else:
                state = "search"
                origin += 1
            #end state down
        elif state == "right":
            if drew:
                delta += 1
            else:
                state = "left"
                delta = -1
            #end state right
        elif state == "left":
            if drew:
                origin -= 1
                lost = False
            else:
                if lost:
                    state = "search"
                    line += 1
                else:
                    state = "down"
                    delta = 0
                    line += 1
            #end state left
        elif state == "search":
            if drew:
                state = "right"
                delta = 1
                lost = False
                full = False
            else:
                if(line > lowest):
                    break
                else:
                    if(lost):
                        if full:
                            #this is a last case scenario for weird triangles
                            origin += 1
                            if (origin > LARGURA):
                                origin = 0
                                line+= 1

                        elif(origin == 0):
                            #scenario: Long thin Triangle... also F this triangle
                            #this case, search every pixel until find one that is drawable
                            line += 1
                            full = True

                        else:  
                            origin -= 1
                    else:
                        lost = True
                        origin -= 1
                        delta = -1
                        state = "left"
            #end state search

        #end of state machine

    print ("Done")
    print (f"Rendered {render_count} pixels")

            
LARGURA = 30
ALTURA = 20

if __name__ == '__main__':
    
    width = LARGURA
    height = ALTURA
    x3d_file = "exemplo3.x3d"
    image_file = "tela.png"

    # Tratando entrada de parâmetro
    parser = argparse.ArgumentParser(add_help=False)   # parser para linha de comando
    parser.add_argument("-i", "--input", help="arquivo X3D de entrada")
    parser.add_argument("-o", "--output", help="arquivo 2D de saída (imagem)")
    parser.add_argument("-w", "--width", help="resolução horizonta", type=int)
    parser.add_argument("-h", "--height", help="resolução vertical", type=int)
    args = parser.parse_args() # parse the arguments
    if args.input: x3d_file = args.input
    if args.output: image_file = args.output
    if args.width: width = args.width
    if args.height: height = args.height
    
    # Iniciando simulação de GPU
    gpu.GPU(width, height)

    # Abre arquivo X3D
    scene = x3d.X3D(x3d_file)
    scene.set_resolution(width, height)

    # funções que irão fazer o rendering
    x3d.X3D.render["Polypoint2D"] = polypoint2D
    x3d.X3D.render["Polyline2D"] = polyline2D
    x3d.X3D.render["TriangleSet2D"] = triangleSet2D

    scene.parse() # faz o traversal no grafo de cena
    interface.Interface(width, height, image_file).preview(gpu.GPU._frame_buffer)
