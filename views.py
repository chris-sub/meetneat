from redis import Redis
redis = Redis()
import time
from functools import update_wrapper
from models import Base, User, Request, Proposal, MealDate
from flask import Flask, jsonify, request, url_for, abort, g, render_template
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine, or_
from flask.ext.cors import CORS, cross_origin


from flask.ext.httpauth import HTTPBasicAuth
import json

#NEW IMPORTS
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
from flask import make_response
import requests

auth = HTTPBasicAuth()


engine = create_engine('sqlite:///meetneat.db')

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
app = Flask(__name__)
cors = CORS(app)

app.config['CORS_HEADERS'] = 'Content-Type'

google_api_key = "AIzaSyDZCCTUOyjR_eJ6JRMm7czb1bQVlNj0F_U"
foursquare_client_id = "4QWURE2Y524UJ01R1UKH3AQ3CB4ES5W3ISEB1OGE4N0RNY3V"
foursquare_client_secret = "H4CEKJZ2MGVGVWJCRLIF2K33EPO53N5VDFJRHJMACMTLWRSO"

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']


class RateLimit(object):
    expiration_window = 10

    def __init__(self, key_prefix, limit, per, send_x_headers):
        self.reset = (int(time.time()) // per) * per + per
        self.key = key_prefix + str(self.reset)
        self.limit = limit
        self.per = per
        self.send_x_headers = send_x_headers
        p = redis.pipeline()
        p.incr(self.key)
        p.expireat(self.key, self.reset + self.expiration_window)
        self.current = min(p.execute()[0], limit)

    remaining = property(lambda x: x.limit - x.current)
    over_limit = property(lambda x: x.current >= x.limit)

def get_view_rate_limit():
    return getattr(g, '_view_rate_limit', None)

def on_over_limit(limit):
    return (jsonify({'data':'You hit the rate limit','error':'429'}),429)

def ratelimit(limit, per=3, send_x_headers=True,
              over_limit=on_over_limit,
              scope_func=lambda: request.remote_addr,
              key_func=lambda: request.endpoint):
    def decorator(f):
        def rate_limited(*args, **kwargs):
            key = 'rate-limit/%s/%s/' % (key_func(), scope_func())
            rlimit = RateLimit(key, limit, per, send_x_headers)
            g._view_rate_limit = rlimit
            if over_limit is not None and rlimit.over_limit:
                return over_limit(rlimit)
            return f(*args, **kwargs)
        return update_wrapper(rate_limited, f)
    return decorator





@app.after_request
def inject_x_rate_headers(response):
    limit = get_view_rate_limit()
    if limit and limit.send_x_headers:
        h = response.headers
        h.add('X-RateLimit-Remaining', str(limit.remaining))
        h.add('X-RateLimit-Limit', str(limit.limit))
        h.add('X-RateLimit-Reset', str(limit.reset))
    return response

@auth.verify_password
def verify_password(username_or_token, password):
    #Try to see if it's a token first
    user_id = User.verify_auth_token(username_or_token)
    if user_id:
        user = session.query(User).filter_by(id = user_id).one()
    else:
        user = session.query(User).filter_by(username = username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True


@app.route('/clientOAuth')
@cross_origin()
def start():
    return render_template('clientOAuth.html')

@app.route('/oauth/<provider>', methods = ['POST'])
@cross_origin()
def login(provider):
    #STEP 1 - Parse the auth code
    auth_code = request.json.get('auth_code')
    print "Step 1 - Complete, received auth code %s" % auth_code
    if provider == 'google':
        #STEP 2 - Exchange for a token
        try:
            # Upgrade the authorization code into a credentials object
            oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
            oauth_flow.redirect_uri = 'postmessage'
            credentials = oauth_flow.step2_exchange(auth_code)
        except FlowExchangeError:
            response = make_response(json.dumps('Failed to upgrade the authorization code.'), 401)
            response.headers['Content-Type'] = 'application/json'
            return response
          
        # Check that the access token is valid.
        access_token = credentials.access_token
        url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
        h = httplib2.Http()
        result = json.loads(h.request(url, 'GET')[1])
        # If there was an error in the access token info, abort.
        if result.get('error') is not None:
            response = make_response(json.dumps(result.get('error')), 500)
            response.headers['Content-Type'] = 'application/json'

        print "Step 2 Complete! Access Token : %s " % credentials.access_token

        h = httplib2.Http()
        userinfo_url =  "https://www.googleapis.com/oauth2/v1/userinfo"
        params = {'access_token': credentials.access_token, 'alt':'json'}
        answer = requests.get(userinfo_url, params=params)
      
        data = answer.json()

        name = data['name']
        picture = data['picture']
        email = data['email']
        
        #see if user exists, if it doesn't make a new one
        user = session.query(User).filter_by(email=email).first()
        if not user:
            user = User(username = name, picture = picture, email = email)
            session.add(user)
            session.commit()

        

        #STEP 4 - Make token
        token = user.generate_auth_token(600)

        

        #STEP 5 - Send back token to the client 
        return jsonify({'token': token.decode('ascii')})
        
        #return jsonify({'token': token.decode('ascii'), 'duration': 600})
    else:
        return 'Unrecoginized Provider'

@app.route('/token')
@cross_origin()
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({'token': token.decode('ascii'), 'user':g.user.id, 'username':g.user.username})

@app.route('/logout')
@cross_origin()
@auth.login_required
def logoff():
    output=g.user.username+" was logged out"
    g.user=None
    return jsonify({'result':output})

@app.route('/api/v1/users', methods = ['POST'])
@cross_origin()
def new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    email=""
    picture=""
    request_json=request.get_json()
    if request_json.has_key('email') and request_json.__getitem__('email') is not None:
        email = request.json.get('email')
    if request_json.has_key('picture') and request_json.__getitem__('picture') is not None:
        picture = request.json.get('picture')
    if username is None or password is None:
        print "missing arguments"
        abort(400) 
    user=session.query(User).filter_by(username = username).first()
    if user is not None:
        print "existing user"
        return jsonify({'message':'user already exists'}), 200#, {'Location': url_for('get_user', id = user.id, _external = True)}
    user = User(username = username)
    user.hash_password(password)
    user.email=email
    user.picture=picture
    session.add(user)
    session.commit()
    return jsonify({ 'id':user.id, 'username': user.username, 'email':user.email, 'picture':user.picture }), 201#, {'Location': url_for('get_user', id = user.id, _external = True)}

@app.route('/api/v1/users', methods=['GET'])
@cross_origin()
@auth.login_required
def get_users():
    users = session.query(User).all()
    if not users:
        abort(400)
    return jsonify({"Users" : [u.serialize for u in users]})

@app.route('/api/v1/users/<int:id>', methods=['GET','PUT', 'DELETE'])
@cross_origin()
@auth.login_required
def handle_user(id):
    user = session.query(User).filter_by(id=id).one()
    if not user:
        abort(400)
    if request.method == "GET":
        return jsonify({'id':user.id,'username': user.username, 'email':user.email, 'picture':user.picture})
    elif request.method == 'PUT':
        request_json=request.get_json()
        if request_json.has_key('username') and request_json.__getitem__('username') is not None:
            user.username=request_json.__getitem__('username')
        if request_json.has_key('email') and request_json.__getitem__('email') is not None:
            user.email=request_json.__getitem__('email')
        if request_json.has_key('picture') and request_json.__getitem__('picture') is not None:
            user.picture=request_json.__getitem__('picture')
        if user.id!=g.user.id:
            abort(400)
        session.commit()
        return jsonify({'result':'changes made'})
    else:
        if user.id==g.user.id:
            session.delete(user)
            session.commit()
            return jsonify({'result':id})
        else:
            abort(400)



def getGeocodeLocation(inputString):
    #Replace Spaces with '+' in URL
    locationString = inputString.replace(" ", "+")
    url = ('https://maps.googleapis.com/maps/api/geocode/json?address=%s&key=%s'% (locationString, google_api_key))
    h = httplib2.Http()
    result = json.loads(h.request(url,'GET')[1])
    #print response
    latitude = result['results'][0]['geometry']['location']['lat']
    longitude = result['results'][0]['geometry']['location']['lng']
    return (latitude,longitude)

def findARestaurant(mealType, location):
    latitude, longitude = getGeocodeLocation(location)
    url = ('https://api.foursquare.com/v2/venues/search?client_id=%s&client_secret=%s&v=20130815&ll=%s,%s&query=%s' % (foursquare_client_id, foursquare_client_secret,latitude,longitude,mealType))
    h = httplib2.Http()
    result = json.loads(h.request(url,'GET')[1])
    if result['response']['venues']:
        #Grab the first restaurant
        restaurant = result['response']['venues'][0]
        venue_id = restaurant['id'] 
        restaurant_name = restaurant['name']
        restaurant_address = restaurant['location']['formattedAddress']
        #Format the Restaurant Address into one string
        address = ""
        for i in restaurant_address:
            address += i + " "
        restaurant_address = address
        
        #Get a  300x300 picture of the restaurant using the venue_id (you can change this by altering the 300x300 value in the URL or replacing it with 'orginal' to get the original picture
        url = ('https://api.foursquare.com/v2/venues/%s/photos?client_id=%s&v=20150603&client_secret=%s' % ((venue_id,foursquare_client_id,foursquare_client_secret)))
        result = json.loads(h.request(url,'GET')[1])
        #Grab the first image
        #if no image available, insert default image url
        if result['response']['photos']['items']:
            firstpic = result['response']['photos']['items'][0]
            prefix = firstpic['prefix']
            suffix = firstpic['suffix']
            imageURL = prefix + "300x300" + suffix
        else:
            imageURL = "http://www.clker.com/cliparts/q/L/P/Y/t/6/no-image-available-md.png"

        restaurantInfo = {'name':restaurant_name, 'address':restaurant_address, 'image':imageURL}
        #print "Restaurant Name: %s " % restaurantInfo['name']
        #print "Restaurant Address: %s " % restaurantInfo['address']
        #print "Image: %s \n " % restaurantInfo['image']
        return restaurantInfo
    else:
        #print "No Restaurants Found for %s" % location
        return "No Restaurants Found"


@app.route('/api/v1/requests', methods = ['POST', 'GET'])
@ratelimit(limit=30, per=30 * 1)
@cross_origin()
@auth.login_required
def handle_requests():
    if request.method== 'POST':
        meal_type=request.json.get('meal_type')
        meal_time=request.json.get('meal_time')
        location_str=request.json.get('location_string')
        longlat=getGeocodeLocation(location_str)
        longitude=longlat[0]
        latitude=longlat[1]
        if location_str is None or meal_type is None:
            print "missing arguments"
            abort(400)
        Req = Request(user_id = g.user.id, location_string=location_str, meal_type=meal_type, meal_time=meal_time, longitude=longitude, latitude=latitude, filled=0)
        session.add(Req)
        session.commit()
        return jsonify({ 'location_string':location_str, 'longitude':longitude, 'meal_time':meal_time, 'latitude':latitude, 'meal_type':meal_type, 'user_id':g.user.id, 'id':Req.id})
    else:
        if request.args.get('all') is None:
            reqs=session.query(Request).filter(Request.user_id != g.user.id).filter(Request.filled!=1).all()
        else:
            reqs=session.query(Request).all()
        return jsonify({"Requests" : [r.serialize for r in reqs]})

@app.route('/api/v1/requests/<int:id>', methods= ['GET', 'PUT','DELETE'])
@ratelimit(limit=30, per=30 * 1)
@cross_origin()
@auth.login_required
def handle_request(id):
    req = session.query(Request).filter_by(id=id).one()
    request_json=request.get_json()
    if not request:
        abort(400)
    if request.method == 'GET':
        return jsonify({'request_id':req.id,'user_id': req.user_id, 'location_string' : req.location_string, 'longitude':req.longitude, 'latitude':req.latitude, 'meal_type' : req.meal_type, 'meal_time':req.meal_time})
    elif request.method == 'PUT':
        if request_json.has_key('filled') and request_json.__getitem__('filled') is not None:
            req.filled=request_json.__getitem__('filled')
        if request_json.has_key('location_string') and request_json.__getitem__('location_string') is not None:
            req.location_string=request_json.__getitem__('location_string')
        if request_json.has_key('meal_type') and request_json.__getitem__('meal_type') is not None:
            req.meal_type=request_json.__getitem__('meal_type')
        if request_json.has_key('meal_time') and request_json.__getitem__('meal_time') is not None:
            req.meal_time=request_json.__getitem__('meal_time')
        if request_json.has_key('longitude') and request_json.__getitem__('longitude') is not None:
            req.longitude=request_json.__getitem__('longitude')
        if request_json.has_key('latitude') and request_json.__getitem__('latitude') is not None:
            req.latitude=request_json.__getitem__('latitude')
        if req.user_id!=g.user.id:
            abort(400)
        session.commit()
        return jsonify({'result':'changes made'})
    else:
        if req.user_id==g.user.id:
            session.delete(req)
            session.commit()
            return jsonify({'result':id})
        else:
            abort(400)

@app.route('/api/v1/proposals', methods = ['POST', 'GET'])
@ratelimit(limit=30, per=30 * 1)
@cross_origin()
@auth.login_required
def handle_proposal():
    if request.method == 'POST':
        request_id=request.json.get('request_id')
        Req=session.query(Request).filter(Request.id == request_id, Request.user_id != g.user.id).first()
        if Req is None or Req.user_id==g.user.id:
            abort(400)
        Prop = Proposal(user_proposed_from = g.user.id, user_proposed_to=Req.user_id, request_id=request_id, filled=0)
        session.add(Prop)
        session.commit()
        return jsonify({ 'user_proposed_from':Prop.user_proposed_from, 'user_proposed_to':Prop.user_proposed_to, 'request_id':Prop.request_id, 'id':Prop.id})
    else:
        props=session.query(Proposal).filter(or_(Proposal.user_proposed_from == g.user.id, Proposal.user_proposed_to == g.user.id)).filter(Proposal.filled!=1).all()
        return jsonify({"Proposals" : [p.serialize for p in props]})

@app.route('/api/v1/proposals/<int:id>', methods= ['GET', 'PUT','DELETE'])
@ratelimit(limit=30, per=30 * 1)
@cross_origin()
@auth.login_required
def handle_proposals(id):
    Prop = session.query(Proposal).filter(Proposal.id==id).one()
    request_json=request.get_json()
    if not Prop:
        abort(400)
    if request.method == 'GET':
        if Prop.user_proposed_from == g.user.id or Prop.user_proposed_to == g.user.id:
            return jsonify({'id':Prop.id, 'user_proposed_to': Prop.user_proposed_to, 'user_proposed_from' : Prop.user_proposed_from, 'request_id' : Prop.request_id, "filled":Prop.filled})
        else:
            abort(400)
    elif request.method == 'PUT':
        if Prop.user_proposed_to == g.user.id: 
            if request_json.has_key('user_proposed_to') and request_json.__getitem__('user_proposed_to') is not None and request_json.__getitem__('user_proposed_to')!=g.user.id:
                Prop.user_proposed_to=request_json.__getitem__('user_proposed_to')
            if request_json.has_key('request_id') and request_json.__getitem__('request_id') is not None and session.query(Request).filter_by(id=request_json.__getitem__('request_id')).one() is not None:
                Prop.request_id=request_json.__getitem__('request_id')
            if request_json.has_key('filled') and request_json.__getitem__('filled') is not None:
                if(request_json.__getitem__('filled')==1 or request_json.__getitem__('filled')=="1"):
                    Prop.filled=1
                    session.commit()
                    Req = session.query(Request).filter_by(id=Prop.request_id).one()
                    Req.filled=1
                    session.commit()
                    Restaurant=findARestaurant(Req.meal_type, Req.location_string)
                    Dateobj = MealDate(user_1 = Prop.user_proposed_to, user_2=Prop.user_proposed_from, restaurant_name=Restaurant['name'], restaurant_address=Restaurant['address'], restaurant_picture=Restaurant['image'], meal_time=Req.meal_time)
                    session.add(Dateobj)
                    session.commit()
                    return jsonify({'result':'changes made to proposal, Date Created'})
                else:
                    session.delete(Prop)
        else:
            return jsonify({'result':'insufficient privileges'})
    else:
        if Prop.user_proposed_to == g.user.id: 
            session.delete(Prop)
            session.commit()
            return jsonify({'result':'successfully deleted '})
        else:
            abort(400)

@app.route('/api/v1/dates', methods = ['POST', 'GET'])
@ratelimit(limit=30, per=30 * 1)
@cross_origin()
@auth.login_required
def handle_dates():
    if request.method == 'POST':
        user_1=request.json.get('user_1')
        user_2=request.json.get('user_2')
        restaurant_name=request.json.get('restaurant_name')
        restaurant_address=request.json.get('restaurant_address')
        restaurant_picture=request.json.get('restaurant_picture')
        meal_time=request.json.get('meal_time')
        if user_1 is None or user_2 is None or restaurant_name is None or restaurant_address is None:
            print "missing arguments"
            abort(400)
        Date = Date(user_1 = user_1, user_2=Date.user_2, restaurant_name=Date.restaurant_name, restaurant_address=Date.restaurant_address, restaurant_picture=Date.restaurant_picture, meal_time=Date.meal_time)
        session.add(Date)
        session.commit()
        return jsonify({ 'user_1':user_1, 'user_2':user_2, 'restaurant_name':restaurant_name, 'restaurant_address':restaurant_address, 'restaurant_picture':restaurant_picture, 'meal_time':meal_time})
    else:
        dates=session.query(MealDate).filter(or_(MealDate.user_1 == g.user.id, MealDate.user_2 == g.user.id)).all()
        return jsonify({"Meal Dates" : [m.serialize for m in dates]})


@app.route('/api/v1/dates/<int:id>', methods= ['GET', 'PUT','DELETE'])
@ratelimit(limit=30, per=30 * 1)
@cross_origin()
@auth.login_required
def handle_date(id):
    Date = session.query(MealDate).filter_by(id=id).one()
    request_json=request.get_json()
    if not Date:
        abort(400)
    if request.method == 'GET':
        if Date.user_1 == g.user.id or Date.user_2 == g.user.id:
            return jsonify({'id':Date.id, 'user_1': Date.user_1, 'user_2':Date.user_2,'meal_time':Date.meal_time,'restaurant_name' : Date.restaurant_address, 'restaurant_address' : Date.restaurant_address, "restaurant_picture":Date.restaurant_picture})
        else:
            abort(400)
    elif request.method == 'PUT':
        if Date.user_1 == g.user.id or Date.user_2 == g.user.id:
            if request_json.has_key('restaurant_name') and request_json.__getitem__('restaurant_name') is not None:
                Date.restaurant_name=request_json.__getitem__('restaurant_name')
            if request_json.has_key('restaurant_address') and request_json.__getitem__('restaurant_address') is not None:
                Date.restaurant_address=request_json.__getitem__('restaurant_address')
            if request_json.has_key('restaurant_picture') and request_json.__getitem__('restaurant_picture') is not None:
                Date.restaurant_picture=request_json.__getitem__('restaurant_picture')
            if request_json.has_key('meal_time') and request_json.__getitem__('meal_time') is not None:
                Date.meal_time=request_json.__getitem__('meal_time')
            return jsonify({'result':'Success'})
        else:
            return jsonify({'result':'insufficient privileges'})
    else:
        if Date.user_1 == g.user.id or Date.user_2 == g.user.id: 
            session.delete(Date)
            session.commit()
            return jsonify({'result':'successfully deleted '})
        else:
            abort(400)



if __name__ == '__main__':
    app.debug = True
    #app.config['SECRET_KEY'] = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    app.run(host='0.0.0.0', port=5000)
