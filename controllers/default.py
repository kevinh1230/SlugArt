# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################
import json
import random

def index():
    images = db().select(db.gallery.ALL, orderby=~db.gallery.time) #display images by upload time. most recent first
    upload = A('Upload', _class='btn',_href=URL('default','upload')) #upload button
    form=FORM('Search:', INPUT (_id = 'search', _name = 'search'), INPUT (_type = 'submit')) #search bar
    if form.process().accepted:
        session.search = request.vars.search #save search query
        redirect(URL('default', 'search')) #redirect to search page
    return dict(images=images,upload=upload,form=form)

#function to get username
def get_username(form):
    if auth.user:
      return auth.user.username
    else:
      form.errors.body = 'Please log in to post a comment' #must be logged in to post comment

def show():
    image = db.gallery(request.args(0,cast=int)) or redirect(URL('index'))
    db.post.imageid.default = image.id
    form = SQLFORM(db.post)
    if form.process(onvalidation=get_username).accepted: #if logged in
        response.flash = 'Your comment is posted' #post comment
    comments = db(db.post.imageid == image.id).select()
    buy = A('Buy This!', _class='btn', _href=URL('index')) #creates a buy button
    upvote = URL('upvote') #call to upvote
    downvote = URL('downvote') #call to downvote
    return dict(image=image, comments=comments, form=form, buy=buy,upvote=upvote,downvote=downvote)

@auth.requires_login()
def upvote():
    s = json.loads(request.vars.msg) or '' #request for string
    myrecord = db(db.gallery.id == s).select().first() #select record to vote for
    if myrecord != None: #if record exists, increment votes by 1
        count = myrecord.likes
        newcounter = count + 1
        db(db.gallery.id == s).update(likes = newcounter)
        mystring = str(newcounter)
    return response.json(dict(result=mystring)) #return string

@auth.requires_login()
def downvote():
    s = json.loads(request.vars.msg) or ''
    myrecord = db(db.gallery.id == s).select().first()
    count = myrecord.likes #get count
    if count <= 0:
        newcounter = 0
        db(db.gallery.id ==s).update(likes = newcounter) #update counter
    else:
        newcounter = count - 1
        db(db.gallery.id ==s).update(likes = newcounter) #update counter
    mystring = str(newcounter) #turn counter to string and return
    return response.json(dict(result=mystring))

@auth.requires_login()
def upload():
    form =SQLFORM(db.gallery)
    r = random.getrandbits(60) #change id to hard to guess number
    form.vars.id = r
    if form.process().accepted:
       session.flash = T('Upload Successful!')
       redirect(URL('default', 'show', args=[form.vars.id, r])) #redirect with two arguments
    return dict(form=form)

#search queries images for title and tag 
def search():
    images = db((db.gallery.title.contains(session.search)) | (db.gallery.tag.contains(session.search))).select(orderby=~db.gallery.time)
    return dict(images = images)

#view logged in users uploads
def youruploads():
    if auth.user: #if logged in
        images = db(db.gallery.uploader == auth.user.username).select(orderby= ~db.gallery.id) #select all images with same username
    else:
        session.flash = ("Please log in") #log in
        redirect(URL('index'))
    return dict(images=images)

#images with digital art category selected
def digitalart():
    images = db(db.gallery.tag == 'Digital Art').select(orderby=~db.gallery.time)
    return dict(images = images)

#images with traditional art catetory selected
def traditional():
    images = db(db.gallery.tag == 'Traditional Art').select(orderby=~db.gallery.time)
    return dict(images = images)

def photography():
    images = db(db.gallery.tag == 'Photography').select(orderby=~db.gallery.time)
    return dict(images = images)

def anime():
    images = db(db.gallery.tag == 'Anime and Manga').select(orderby=~db.gallery.time)
    return dict(images = images)

def cartoons():
    images = db(db.gallery.tag == 'Cartoons').select(orderby=~db.gallery.time)
    return dict(images = images)

def scraps():
    images = db(db.gallery.tag == 'Scraps').select(orderby=~db.gallery.time)
    return dict(images = images)

def fanart():
    images = db(db.gallery.tag == 'Fan Art').select(orderby=~db.gallery.time)
    return dict(images = images)

#images ordered from highest votes
def highestvoted():
    images = db().select(db.gallery.ALL, orderby=~db.gallery.likes)
    return dict(images=images)

#about us page
def about_us():
    return dict()

#privacy page
def privacy():
    return dict()

#purchase confirmation page
def purchase_confirmation():
    return dict()

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())

@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_signature()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id]
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs must be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())
