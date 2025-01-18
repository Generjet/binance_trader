# -*- encoding: utf-8 -*-
"""
Blog Module
"""
from flask import Blueprint

blog_bp = Blueprint('blog', __name__, 
                   template_folder='templates',
                   static_folder='static',
                   url_prefix='/blog')

from . import routes
