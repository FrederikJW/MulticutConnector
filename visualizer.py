import math
import sys
from typing import Union

import numpy as np
import pygame
from pygame import gfxdraw

from constants import *
from graph import Graph
import threading


class Visualizer:
    def __init__(self, drawing_lock):
        self.graph = None
        self.drawing_lock = drawing_lock

        # setup pygame
        pygame.init()
        self.clock = pygame.time.Clock()

        # setup screen
        self.screen_size = SCREEN_SIZE
        self.screen = pygame.display.set_mode(self.screen_size, pygame.RESIZABLE)
        pygame.display.set_caption("Shortest Path Multicut")
        self.screen.fill(WHITE)
        self.surface = pygame.Surface(self.screen_size)
        self.surface.fill(WHITE)

        # setup text
        self.font = pygame.font.SysFont('Ariel', 32)
        waiting_text = self.font.render("Waiting for graph", True, BLACK)
        waiting_text_rec = waiting_text.get_rect()
        waiting_text_rec.center = tuple(np.round((np.array(self.screen_size) / 2)).astype(int))

        # draw init screen
        self.screen.blit(waiting_text, waiting_text_rec)
        pygame.display.update()

        self.scale = 1
        self.offset = (0, 0)
        self.set_scale()

    def run(self):
        while True:
            events = pygame.event.get()
            pygame.event.pump()
            for event in events:
                if event.type == pygame.QUIT:
                    self.quit()
                elif event.type == pygame.VIDEORESIZE:
                    self.screen_size = event.dict['size']
                    self.surface = pygame.Surface(self.screen_size)
                    self.surface.fill(COLOR_KEY)
                    self.set_scale()

            if self.graph is not None:
                with self.drawing_lock:
                    self.surface.fill(COLOR_KEY)
                    self.draw_graph()

                    self.screen.fill(WHITE)
                    self.screen.blit(self.surface, (0, 0))

                    pygame.display.update()

            self.clock.tick(FRAMES_PER_SECOND)

    def quit(self):
        pygame.quit()
        sys.exit()

    def set_graph(self, graph: Graph):
        with self.drawing_lock:
            self.graph = graph
            self.set_scale()

    def set_scale(self):
        if self.graph is None:
            return

        max_x = max(map(lambda x: x[1][0], self.graph.nodes(data="pos")))
        max_y = max(map(lambda x: x[1][1], self.graph.nodes(data="pos")))
        width = self.screen_size[0]
        height = self.screen_size[1]

        if max_x / max_y > width / height:
            # x and width is limiting
            margin = width * 0.05
            graph_width = width - margin * 2
            self.scale = graph_width / max_x
            self.offset = np.array((margin, (height - max_y * self.scale) / 2))
        else:
            # y and height is limiting
            margin = height * 0.05
            graph_height = height - margin * 2
            self.scale = graph_height / max_y
            self.offset = np.array(((width - max_x * self.scale) / 2, margin))

    def draw_graph(self):
        self.surface.fill(COLOR_KEY)
        node_radius = self.scale_value(GRAPH_NODE_RADIUS)
        edge_width = self.scale_value(GRAPH_EDGE_WIDTH)

        # draw edges
        for edge in self.graph.edges.data("cost"):
            self.draw_thick_aaline(self.scale_value(self.graph.nodes[edge[0]]['pos']),
                                   self.scale_value(self.graph.nodes[edge[1]]['pos']),
                                   GREEN if edge[2] == 1 else RED,
                                   edge_width)

        # draw nodes
        for node, pos in self.graph.nodes(data="pos"):
            pos = tuple(self.scale_value(pos))
            gfxdraw.aacircle(self.surface, *pos, node_radius, DARK_BLUE)
            gfxdraw.filled_circle(self.surface, *pos, node_radius, DARK_BLUE)

    def scale_value(self, value: Union[np.ndarray, float, int]):
        if value.__class__ == np.ndarray:
            return np.round(value * self.scale + self.offset).astype(int)
        else:
            result = round(value * self.scale)
            return result if result > 0 else 1

    # draw an anti-aliased line with thickness more than 1px
    # reference: https://stackoverflow.com/a/30599392
    def draw_thick_aaline(self, pos1: np.ndarray, pos2: np.ndarray, color, width):
        centerx, centery = tuple((pos1 + pos2) / 2)
        length = math.hypot(*(pos2 - pos1))
        angle = math.atan2(pos1[1] - pos2[1], pos1[0] - pos2[0])
        width2, length2 = width / 2, length / 2
        sin_ang, cos_ang = math.sin(angle), math.cos(angle)

        width2_sin_ang = width2 * sin_ang
        width2_cos_ang = width2 * cos_ang
        length2_sin_ang = length2 * sin_ang
        length2_cos_ang = length2 * cos_ang

        ul = (centerx + length2_cos_ang - width2_sin_ang,
              centery + width2_cos_ang + length2_sin_ang)
        ur = (centerx - length2_cos_ang - width2_sin_ang,
              centery + width2_cos_ang - length2_sin_ang)
        bl = (centerx + length2_cos_ang + width2_sin_ang,
              centery - width2_cos_ang + length2_sin_ang)
        br = (centerx - length2_cos_ang + width2_sin_ang,
              centery - width2_cos_ang - length2_sin_ang)

        gfxdraw.aapolygon(self.surface, (ul, ur, br, bl), color)
        gfxdraw.filled_polygon(self.surface, (ul, ur, br, bl), color)
