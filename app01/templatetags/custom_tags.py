# myapp/templatetags/custom_tags.py
from django import template
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from app01.models import Comment
from datetime import datetime
register = template.Library()

@register.simple_tag(takes_context=True)
def render_comments(context, article):
    comments = Comment.objects.filter(article=article, parent=None)
    return mark_safe(_render_comments(context, comments))

def _render_comments(context, comments, level=0):
    html = ''
    for comment in comments:
        level_class = f'level-{level}'
        # Determine background color based on level
        if level == 0:
            background_color = '#f8f9fa'  # Light gray
        elif level == 1:
            background_color = '#e9ecef'  # Light blue-gray
        elif level == 2:
            background_color = '#dee2e6'  # Light gray-blue
        else:
            # For levels beyond 2, alternate colors or define additional colors
            if level % 2 == 0:
                background_color = '#f0f0f0'  # Alternate color 1
            else:
                background_color = '#f5f5f5'  # Alternate color 2
        # Format the publish_time using strftime
        formatted_time = comment.publish_time.strftime('%Y-%m-%d %H:%M:%S')
        html += f'<div class="list-group-item comment {level_class}" style="margin-left: {level * 20}px; background-color: {background_color};">'
        html += f'<div class="comment-content-reply" style="display:flex">'
        html += f'<div class="comment-content">'
        html += f'<strong>{comment.author.username}</strong> | <small class="text-muted">{formatted_time}</small>'
        html += f'<p class="mt-2">{comment.content}</p>'
        html += f'</div>'
        # if user.is_authenticated:
        html += f'<button class="btn reply-btn" data-comment-id="{comment.id}" style="display: none;" >Reply</button>'
        html += f'</div>'
        if comment.replies.count() > 0:
            html += '<div class="replies">'
            html += _render_comments(context, comment.replies.all(), level + 1)
            html += '</div>'

        context['comment'] = comment
        context_dict = context.flatten()
        html += render_to_string('reply_form.html', context_dict)
        html += '</div>'

    return html
