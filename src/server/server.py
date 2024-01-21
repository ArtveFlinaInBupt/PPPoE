from .algo import *
from config.project_meta import __project__

from sanic import Sanic, response
from sanic.worker.loader import AppLoader
from sanic.log import logger
from functools import partial

import asyncio


def create_app():
    app = Sanic(f'{__project__}S')
    app.ctx.data_accessor = DataAccessor()

    @app.get('/ping')
    async def ping_handler(request):
        arg: str = request.args.get('arg', 'ping')
        return response.text(
            arg.replace('i', 'o').replace('I', 'O')
        )

    @app.post('/api/total')
    async def total_handler(request):
        logger.log(logging.INFO, f'/api/total: {request.json}')
        try:
            points = request.json.get('geometry')['coordinates'][0]
            if len(points) < 3:
                raise Exception('Too few points.')

            convex = calc_convex(list(Point2D(p[0], p[1]) for p in points))

            loop = asyncio.get_event_loop()
            ans = await loop.run_in_executor(
                None, calc_whole_convex, convex, app.ctx.data_accessor
            )

            logger.debug(f'convex: {convex}, ans: {ans}')
            return response.json({
                'convex': [[p.x, p.y] for p in convex],
                'population': ans
            })

        except Exception as e:
            logger.fatal(f'/api/total: {e.__repr__()}', exc_info=True)
            return response.json({
                'error': str(e)
            })

    @app.post('/api/grid')
    async def grid_handler(request):
        logger.log(logging.INFO, f'/api/grid: {request.json}')
        try:
            points = request.json.get('geometry')['coordinates'][0]
            width = request.json.get('grid_width')

            if len(points) < 3:
                raise Exception('Too few points.')
            if width < 1:
                raise Exception('Grid width must be positive.')

            min_x = min(p[0] for p in points)
            max_x = max(p[0] for p in points)
            min_y = min(p[1] for p in points)
            max_y = max(p[1] for p in points)

            convex = calc_convex(list(Point2D(p[0], p[1]) for p in points))

            cache = {}
            ans_mat = []
            for x in range(min_x, max_x + 1, width):
                ans_mat.append([])
                for y in range(min_y, max_y + 1, width):
                    square = [
                        Point2D(x, y), Point2D(x + width, y),
                        Point2D(x, y + width), Point2D(x + width, y + width)
                    ]

                    valid = False
                    for p in square:
                        if p not in cache:
                            cache[p] = await (asyncio.get_event_loop()
                                              .run_in_executor(
                                None, point_in_convex, p, convex)
                            )
                        if cache[p]:
                            valid = True
                            break
                    if not valid:
                        ans_mat[-1].append(-1)
                        continue

                    ans = 0
                    conv = calc_convex(square)
                    loop = asyncio.get_event_loop()
                    ans += await loop.run_in_executor(
                        None, calc_whole_convex,
                        conv, app.ctx.data_accessor
                    )
                    ans_mat[-1].append(ans)

            return response.json({
                'grid': ans_mat,
            })

        except Exception as e:
            logger.fatal(f'/api/grid: {e.__repr__()}', exc_info=True)
            return response.json({
                'error': str(e)
            })

    return app


class Server:
    def __init__(self, port: int):
        self.loader = AppLoader(factory=partial(create_app))
        self.app = self.loader.load()
        self.app.prepare(host='0.0.0.0', port=port, dev=True)

    def run(self):
        Sanic.serve(primary=self.app, app_loader=self.loader)
