from functools import wraps
from django.contrib.sessions.backends.db import SessionStore
from rest_framework.response import Response
from rest_framework import status

def verified_user(user_type_id_required, user_type_required):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            session_id = request.GET.get('session_id')
            if not session_id:
                return Response({"error": "session_id not provided"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                session = SessionStore(session_key=session_id)
                session_data = session.load()
            except Exception:
                return Response({"error": "Invalid session_id"}, status=status.HTTP_400_BAD_REQUEST)

            if session_data.get("user_type_id") != user_type_id_required or session_data.get("user_type") != user_type_required:
                return Response({"error": f"{user_type_required} not found."}, status=status.HTTP_403_FORBIDDEN)

            return view_func(request, *args, **kwargs)

        return _wrapped_view
    return decorator
