from flask import Blueprint, jsonify, request
from app.services.job_view_service import JobViewService
from app.utils.decorators import admin_required
from app.utils.helpers import api_response

job_view_bp = Blueprint('job_views', __name__, url_prefix='/job_views')

@job_view_bp.route('/monthly', methods=['GET'])
@admin_required
def get_monthly_job_views():
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)

    if not year or not month:
        return api_response(400, "Year and month are required parameters.")

    monthly_views = JobViewService.get_monthly_views(year, month)
    
    result = []
    for job_id, total_views in monthly_views:
        result.append({'job_id': job_id, 'total_views': total_views})

    return api_response(200, "Monthly job views retrieved successfully", result)
