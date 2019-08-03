import sys
import os

sys.path.append('../')
sys.path.append('./')

from falcon_routing_tools import Router

def test_router_resource_decorator():
    router = Router()

    @router.resource('/some-path')
    class SomeResource():
        pass

    assert len(router.resources) == 1
    route = router.resources[0]
    assert route.path == '/some-path'
    assert route.resource.__name__ == 'SomeResource'

def test_controller_loading():
    from fixtures.router import router

    base_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'fixtures')
    router.load_controllers(base_dir)

    assert len(router.resources) == 3
    expected_paths = set(['/resource-a', '/resource-a/{id}', '/resource-b'])
    actual_paths = set([route.path for route in router.resources])
    assert expected_paths == actual_paths