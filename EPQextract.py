import pygame
import random

pygame.init()
pygame.font.init()
my_font = pygame.font.SysFont('Arial', 20)
dimensions = (1280,720)
bounds = (1152, 648)
screen = pygame.display.set_mode(dimensions)
    
radius = 10
cuecoords = (random.randint((dimensions[0]-bounds[0])//2+1,bounds[0]-1), random.randint((dimensions[1]-bounds[1])//2+1,bounds[1]-1))

class Node:
    def __init__(self, name, coords):
        self.coords = coords
        self.name = name

cue = Node("CUE", cuecoords)
holes = [Node("HOLE", (600,100))]
balls = [Node("A", (1000, 600)), 
        Node("B", (800, 150)),
        Node("C", (850, 500)),
        Node("D", (200, 250)),
        Node("E", (400, 550)),
        Node("F", (100, 600))]

def allPaths(start, end, path=[]):
    path = path + [start]

    if start == end and len(path) > 2:
        return [path]

    all_paths = []
    for ball in balls + [cue]:
        if ball not in path:
            if len(path) == 1 or determineParent(path[-2].coords, start.coords, ball.coords):
                new_paths = allPaths(ball, end, path)
                all_paths.extend(new_paths)
            newstart = start.coords if len(path) == 1 else computeNewStart(path[-2].coords, start.coords)
            bouncepoints = calculateBouncePoints(newstart, ball.coords)
            for bouncepoint in bouncepoints:
                bounce = Node("BOUNCE", bouncepoint)
                if len(path) == 1 or determineParent(path[-2].coords, start.coords, bounce.coords):
                    new_paths = allPaths(ball, end, path + [bounce])
                    all_paths.extend(new_paths)

    return all_paths

def calculateDistance(start, end):
    return ((end[1]-start[1])**2+(end[0]-start[0])**2)**(1/2)

def calculateMidpoint(start, end):
    return (start[0]-(start[0]-end[0])/2, start[1]-(start[1]-end[1])/2)

def calculateBouncePoint(coordsA, coordsB):
    Ax, Ay = coordsA
    Bx, By = coordsB
    return ((Bx*Ay+Ax*By)/(Ay+By), 0)

def calculateBouncePoints(coordsA, coordsB):
    Ax, Ay = coordsA
    Bx, By = coordsB
    horizontalx = (Bx*Ay+Ax*By)/(Ay+By)
    verticaly = (Ax*By+Ay*Bx)/(Ax+Bx)
    
    #Include 2 boundaries:
    #return [(horizontalx, (dimensions[0]-bounds[0])/2), (horizontalx, bounds[1])]
    
    #Include all 4 boundaries (resource intensive):
    return [(horizontalx, (dimensions[0]-bounds[0])/2), (horizontalx, bounds[1]), ((dimensions[1]-bounds[1])/2, verticaly), (bounds[0], verticaly)]


def computeNewStart(startCoords, circleCoords):
    r = radius * 2
    m, n = startCoords
    a, b = circleCoords
    x = a - r*(m-a)/((n-b)**2+(m-a)**2)**(1/2)
    y = b - r*(n-b)/((n-b)**2+(m-a)**2)**(1/2)
    return (x,y)
    
    
def determineParent(startCoords, circleCoords, newCircleCoords):
    newStartCoords = computeNewStart(startCoords, circleCoords)
    m, n = startCoords
    a, b = circleCoords
    x1, y1 = newStartCoords
    x, y = newCircleCoords
    if n-b != 0:
        grad = (a-m)/(n-b)
        yBound = grad*(x-x1)+y1
        return y <= yBound if b >= y1 else y >= yBound
    return x <= x1 if a >= x1 else x >= x1

screen.fill("white")

paths = [path for path in allPaths(holes[0], cue) if [ball.name for ball in path] not in [["HOLE", "BOUNCE", "CUE"],["HOLE", "CUE"]]]
if len(paths) > 0:
    mindistance = (float("inf"), paths[0])
    maxdistance = (0, paths[0], 0)
    for path in paths:
        end = holes[0].coords
        distance = 0
        for i in range(1,len(path)):
            start = end
            if path[i].name != "BOUNCE":
                end = computeNewStart(start, path[i].coords)
            else:
                end = path[i].coords
            pygame.draw.line(screen, (200, 200, 200), start, end, 1)
            pygame.draw.circle(screen, (255, 0, 0), end, 3, 0)
            bouncepoint = calculateBouncePoint(start, end)
            distance += calculateDistance(start, end)
            label = my_font.render(str(round(calculateDistance(start, end), 2)), False, (0, 0, 0))
            screen.blit(label, calculateMidpoint(start, end))
        if distance < mindistance[0]:
            mindistance = (distance, path)
        if distance > maxdistance[0]:
            maxdistance = (distance, path)
    
    end = holes[0].coords
    print(mindistance[0], [x.name for x in mindistance[1]])
    for i in range(1, len(mindistance[1])):
        start = end
        if mindistance[1][i].name != "BOUNCE":
            end = computeNewStart(start, mindistance[1][i].coords)
        else:
            end = mindistance[1][i].coords
        pygame.draw.line(screen, (0,255,0), start, end, 4)
    end = holes[0].coords
    for i in range(1, len(maxdistance[1])):
        start = end
        if maxdistance[1][i].name != "BOUNCE":
            end = computeNewStart(start, maxdistance[1][i].coords)
        else:
            end = maxdistance[1][i].coords
        pygame.draw.line(screen, (255,165,0), start, end, 4)
        
pygame.draw.circle(screen, (0, 0, 0), holes[0].coords, radius, 0)
pygame.draw.circle(screen, (0, 0, 0), cue.coords, radius, 1)
for ball in balls:
    pygame.draw.circle(screen, (0, 0, 255), ball.coords, radius, 0)
    pygame.draw.circle(screen, (0, 0, 255), ball.coords, radius * 2, 1)
    label = my_font.render(ball.name, False, (0, 0, 0))
    screen.blit(label, ball.coords)


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
    pygame.display.flip() 
    
        