import sys

sys.path.append('../')
sys.path.append('./')

from fixtures.router import router

@router.resource('/resource-a')
class ResourceA():
    pass

@router.resource('/resource-a/{id}')
class ResourceAId():
    pass