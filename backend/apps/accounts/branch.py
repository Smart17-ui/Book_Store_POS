from rest_framework.exceptions import PermissionDenied

from .models import Branch


def request_branch(request):
    if request.user.branch_id:
        return request.user.branch
    branch_id = request.headers.get('X-Branch-ID')
    if branch_id:
        branch = Branch.objects.filter(id=branch_id, client_id=request.user.client_id, is_active=True).first()
        if not branch:
            raise PermissionDenied('The selected branch is not available to your company.')
        return branch
    return Branch.objects.filter(client_id=request.user.client_id, is_active=True).order_by('name').first()