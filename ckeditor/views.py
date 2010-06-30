import os

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
            
try: 
    from PIL import Image, ImageOps 
except ImportError: 
    import Image, ImageOps

try:
    from django.views.decorators.csrf import csrf_exempt
except ImportError:
    # monkey patch this with a dummy decorator which just returns the same function
    # (for compatability with pre-1.1 Djangos)
    def csrf_exempt(fn):
        return fn
        
THUMBNAIL_SIZE = (75, 75)
    
def exists(name):
    """
    Determines wether or not a file exists on the target storage system.
    """
    return os.path.exists(name)

def get_available_name(name):
    """
    Returns a filename that's free on the target storage system, and
    available for new content to be written to.
    """
    dir_name, file_name = os.path.split(name)
    file_root, file_ext = os.path.splitext(file_name)
    # If the filename already exists, keep adding an underscore (before the
    # file extension, if one exists) to the filename until the generated
    # filename doesn't exist.
    while exists(name):
        file_root += '_'
        # file_ext includes the dot.
        name = os.path.join(dir_name, file_root + file_ext)
    return name

def get_thumb_filename(filename):
    """
    Generate thumb filename by adding _thumb to end of filename before . (if present)
    """
    try:
        dot_index = filename.rindex('.')
    except ValueError: # filename has no dot
        return '%s_thumb' % filename
    else:
        return '%s_thumb%s' % (filename[:dot_index], filename[dot_index:])

def create_thumbnail(filename):
    image = Image.open(filename)
        
    # Convert to RGB if necessary
    # Thanks to Limodou on DjangoSnippets.org
    # http://www.djangosnippets.org/snippets/20/
    if image.mode not in ('L', 'RGB'):
        image = image.convert('RGB')
       
    # scale and crop to thumbnail
    imagefit = ImageOps.fit(image, THUMBNAIL_SIZE, Image.ANTIALIAS)
    imagefit.save(get_thumb_filename(filename))
        
def get_media_url(path, username=""):
    """
    Determine system file's media url.
    """
    upload_url = getattr(settings, "CKEDITOR_UPLOAD_PREFIX", None)
    userdir = username and username + "/" or ""
    if upload_url:
        url = upload_url + userdir + os.path.basename(path)
    else:
        url = settings.MEDIA_URL + userdir + path.split(settings.MEDIA_ROOT)[1]
    return url

def get_user_dir(username):
    basedir = os.path.join(settings.CKEDITOR_UPLOAD_PATH, username)
    if not os.path.isdir(basedir):
        os.mkdir(basedir)
    return basedir

@csrf_exempt
def upload(request):
    """
    Uploads a file and send back its URL to CKEditor.

    TODO:
        Validate uploads
    """
    # get the upload from request
    upload = request.FILES['upload']

    # determine destination filename
    if getattr(settings, "CKEDITOR_PER_USER", False):
        destination_filename = get_available_name(os.path.join(get_user_dir(request.user.username), upload.name))
    else:
        destination_filename = get_available_name(os.path.join(settings.CKEDITOR_UPLOAD_PATH, upload.name))
     
    # iterate through chunks and write to destination
    destination = open(destination_filename, 'wb+')
    for chunk in upload.chunks():
        destination.write(chunk)
    destination.close()

    create_thumbnail(destination_filename)

    url = get_media_url(destination_filename, getattr(settings, "CKEDITOR_PER_USER", False) and request.user.username)

    # respond with javascript sending ckeditor upload url, if present, otherwise return the browse request
    if request.GET.get('CKEditorFuncNum', ""):
        return HttpResponse("""
        <script type='text/javascript'>
            window.parent.CKEDITOR.tools.callFunction(%s, '%s');
        </script>""" % (request.GET['CKEditorFuncNum'], url))
    else:
        return browse(request, selected_filename=destination_filename)

def browse(request, selected_filename=None, callback=None):
    if getattr(settings, "CKEDITOR_PER_USER", False):
        uploads = os.listdir(get_user_dir(request.user.username))
    else:
        uploads = os.listdir(settings.CKEDITOR_UPLOAD_PATH)
    
    images = []
    for upload in uploads:
        # bypass for thumbs
        if '_thumb' in upload:
            continue
        if getattr(settings, "CKEDITOR_PER_USER", False):
            filename = os.path.join(get_user_dir(request.user.username), upload)
        else:
            filename = os.path.join(settings.CKEDITOR_UPLOAD_PATH, upload)
	print filename
        images.append({
            'thumb': get_media_url(get_thumb_filename(filename), getattr(settings, "CKEDITOR_PER_USER", False) and request.user.username),
            'src': get_media_url(filename, getattr(settings, "CKEDITOR_PER_USER", False) and request.user.username),
            'selected': (selected_filename == filename and "selected" or "")
        })
   
    context = RequestContext(request, {
        'images': images,
        'media_prefix': settings.CKEDITOR_MEDIA_PREFIX,
        'callback': request.GET.get("callback", ""),
        'CKEditor': request.GET.get("CKEditor", ""),
        'CKEditorFuncNum': request.GET.get("CKEditorFuncNum", ""),
    })
    return render_to_response('browse.html', context)
