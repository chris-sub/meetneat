function timeConverter(UNIX_timestamp){
  var a = new Date(UNIX_timestamp * 1000);
  var months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  var year = a.getFullYear();
  var month = months[a.getMonth()];
  var date = a.getDate();
  var hour = a.getHours();
  var min = a.getMinutes();
  var sec = a.getSeconds();
  var time = date + ' ' + month + ' ' + year + ' ' + hour + ':' + min + ':' + sec ;
  return time;
}
var Base64 = {


    _keyStr: "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=",


    encode: function(input) {
        var output = "";
        var chr1, chr2, chr3, enc1, enc2, enc3, enc4;
        var i = 0;

        input = Base64._utf8_encode(input);

        while (i < input.length) {

            chr1 = input.charCodeAt(i++);
            chr2 = input.charCodeAt(i++);
            chr3 = input.charCodeAt(i++);

            enc1 = chr1 >> 2;
            enc2 = ((chr1 & 3) << 4) | (chr2 >> 4);
            enc3 = ((chr2 & 15) << 2) | (chr3 >> 6);
            enc4 = chr3 & 63;

            if (isNaN(chr2)) {
                enc3 = enc4 = 64;
            } else if (isNaN(chr3)) {
                enc4 = 64;
            }

            output = output + this._keyStr.charAt(enc1) + this._keyStr.charAt(enc2) + this._keyStr.charAt(enc3) + this._keyStr.charAt(enc4);

        }

        return output;
    },


    decode: function(input) {
        var output = "";
        var chr1, chr2, chr3;
        var enc1, enc2, enc3, enc4;
        var i = 0;

        input = input.replace(/[^A-Za-z0-9\+\/\=]/g, "");

        while (i < input.length) {

            enc1 = this._keyStr.indexOf(input.charAt(i++));
            enc2 = this._keyStr.indexOf(input.charAt(i++));
            enc3 = this._keyStr.indexOf(input.charAt(i++));
            enc4 = this._keyStr.indexOf(input.charAt(i++));

            chr1 = (enc1 << 2) | (enc2 >> 4);
            chr2 = ((enc2 & 15) << 4) | (enc3 >> 2);
            chr3 = ((enc3 & 3) << 6) | enc4;

            output = output + String.fromCharCode(chr1);

            if (enc3 != 64) {
                output = output + String.fromCharCode(chr2);
            }
            if (enc4 != 64) {
                output = output + String.fromCharCode(chr3);
            }

        }

        output = Base64._utf8_decode(output);

        return output;

    },

    _utf8_encode: function(string) {
        string = string.replace(/\r\n/g, "\n");
        var utftext = "";

        for (var n = 0; n < string.length; n++) {

            var c = string.charCodeAt(n);

            if (c < 128) {
                utftext += String.fromCharCode(c);
            }
            else if ((c > 127) && (c < 2048)) {
                utftext += String.fromCharCode((c >> 6) | 192);
                utftext += String.fromCharCode((c & 63) | 128);
            }
            else {
                utftext += String.fromCharCode((c >> 12) | 224);
                utftext += String.fromCharCode(((c >> 6) & 63) | 128);
                utftext += String.fromCharCode((c & 63) | 128);
            }

        }

        return utftext;
    },

    _utf8_decode: function(utftext) {
        var string = "";
        var i = 0;
        var c = c1 = c2 = 0;

        while (i < utftext.length) {

            c = utftext.charCodeAt(i);

            if (c < 128) {
                string += String.fromCharCode(c);
                i++;
            }
            else if ((c > 191) && (c < 224)) {
                c2 = utftext.charCodeAt(i + 1);
                string += String.fromCharCode(((c & 31) << 6) | (c2 & 63));
                i += 2;
            }
            else {
                c2 = utftext.charCodeAt(i + 1);
                c3 = utftext.charCodeAt(i + 2);
                string += String.fromCharCode(((c & 15) << 12) | ((c2 & 63) << 6) | (c3 & 63));
                i += 3;
            }

        }

        return string;
    }

}
    
    
    



function delRequest($http, $scope, id)
{
	var authdata=Base64.encode('admin:123456');
	$http.defaults.headers.common['Authorization'] = 'Basic ' + authdata;
	$http({
	  method: 'DELETE',
	  url: 'http://localhost:5000/api/v1/requests/'+id
	}).then(function successCallback(response) {
	    // this callback will be called asynchronously
	    // when the response is available
	    console.log(response)
	  }, function errorCallback(response) {
	  	alert("ERRORS!");
	    // called asynchronously if an error occurs
	    // or server returns response with an error status.
	  });

}

/**************************/

var app=angular.module('myApp',['ngRoute']); 
app.config(function($routeProvider) {
	$routeProvider
	.when('/', {
		templateUrl:'partials/main'
	})

	.when('/register', {
		templateUrl:'partials/register',
		controller:'userController'
	})

	.when('/requests', {
		templateUrl:'partials/requests',
		controller:'requestController'
	})

	.when('/proposals', {
		templateUrl:'partials/proposals',
		controller:'proposalController'
	})

	.when('/dates', {
		templateUrl:'partials/dates',
		controller:'mealDateController'
	})
	.otherwise({redirectTo:'/'});
});

app.controller('mainController', function($scope, $http, $window)
{
	$scope.showloginform=function()
	{
		var loginMessage=document.getElementById("loggedin").getElementsByClassName("user").item(0);
		if(loginMessage.innerHTML.length>13)
		{
			$("#loggedin").fadeOut("slow", function () {
				loginMessage.innerHTML="Logged in as ";
				$("#login").fadeIn()
			});
		}
	}
	$scope.hideloginform=function(username) {
		var loginMessage=document.getElementById("loggedin").getElementsByClassName("user").item(0);
		if(loginMessage.innerHTML.length<=13)
		{
		$("#login").fadeOut("slow", function () {
			if(username!="") loginMessage.innerHTML="Logged in as "+username;
			$("#loggedin").fadeIn()
		});
		}
	}
	$scope.login=function (user)
	{
		$http({
	  	method: 'GET',
	  	url: 'http://localhost:5000/token',
	  	headers: {'Authorization':'Basic '+Base64.encode(user.username+':'+user.password)}
		}).then(function successCallback(response) {
	    $scope.hideloginform(response.data.username);
	    localStorage.setItem("user", JSON.stringify(response.data));
	    user.username="";
	    user.password="";
	    $window.location.href = '/';
	  	}, function errorCallback(response) {
	  	alert("ERRORS!");
	    // called asynchronously if an error occurs
	    // or server returns response with an error status.
	  });
	};
	
	if(window.localStorage && window.localStorage.getItem('user')!==null)
	{
		$scope.hideloginform(JSON.parse(window.localStorage.getItem('user')).username);
	}
	else
	{
		$scope.showloginform();
	}
	$scope.logout=function ()
	{
		$scope.showloginform();
		$http({
	  	method: 'GET',
	  	headers: {'Content-type':'application/json', 'Authorization':'Basic '+Base64.encode(JSON.parse(localStorage.getItem("user")).token+':""')},
	  	url: 'http://localhost:5000/logout'
		}).then(function successCallback(response) {
		    console.log(response);
		    window.localStorage.removeItem('user');
	  	}, function errorCallback(response) {
	  		window.localStorage.removeItem('user');
	    // called asynchronously if an error occurs
	    // or server returns response with an error status.
	  });
	};
});

app.controller('requestController', function($scope, $http, $routeParams, $window)
{
	$scope.master = {};
	$scope.message='request';
	$scope.timeConverter=timeConverter;
	$scope.del=function (item)
	{
		$http({
		method: 'DELETE',
		url: 'http://localhost:5000/api/v1/requests/'+item.id,
		headers: {'Content-type':'application/json', 'Authorization':'Basic '+Base64.encode(JSON.parse(localStorage.getItem("user")).token+':""')}
		}).then(function successCallback(response) {
		    var index = $scope.myrequests.indexOf(item);
  			$scope.myrequests.splice(index, 1); 
		  }, function errorCallback(response) 
		  {
		  	console.log(response);
		  });

	};
	$scope.getCoordinates=function(item)
	{
		if(item.location_string!=undefined&&item.location_string!="")
		$http({
		  method: 'GET',
		  url: 'https://maps.googleapis.com/maps/api/geocode/json?address='+item.location_string+'&key=AIzaSyDZCCTUOyjR_eJ6JRMm7czb1bQVlNj0F_U'
		}).then(function successCallback(response) {
		    if(response.data.status=="OK")
			{
				item.longitude=response.data.results[0].geometry.location.lng;
				item.latitude=response.data.results[0].geometry.location.lat;
			}
		  }, function errorCallback(response) {
		  	console.log(response);
		  });
	}

	$scope.add=function (item)
	{
		$http({
	  	method: 'POST',
	  	url: 'http://localhost:5000/api/v1/requests',
	 	data: '{"location_string":"'+item.location_string+'","meal_type":"'+item.meal_type+'","meal_time":"'+item.meal_time+'", "longitude":"'+item.longitude+'", "latitude":"'+item.latitude+'", "user_id":"'+JSON.parse(window.localStorage.getItem('user')).id+'"}',
	  	// data: '{"location":"'+item.location_string+'","meal_type":"'+item.meal_type+'","meal_time":"'+item.meal_time+'", "longitude":"'+item.longitude+'", "latitude":"'+item.latitude+'", "user_id":"2"}',
	  	headers: {'Content-type':'application/json', 'Authorization':'Basic '+Base64.encode(JSON.parse(localStorage.getItem("user")).token+':""')}
		}).then(function successCallback(response) {
	    $scope.myrequests.push(response.data);
	    alert("Request added successfully");
	    //$scope.requests=response.data.Requests;
	  	}, function errorCallback(response) {
	  	alert("ERRORS!");
	    // called asynchronously if an error occurs
	    // or server returns response with an error status.
	  });

	}
	$scope.edit=function(item)
	{
		angular.element(document.getElementById("requestForm")).scope().req=item;
	}
	$scope.reset=function(req)
	{
		angular.element(document.getElementById("requestForm")).scope().req={"id":"","meal_type":"","meal_time":"","location_string":""};
		console.log($scope);
        req.meal_time = "";
        req.id="";
        req.meal_type="";
        req.longitude="";
        req.latitude="";
        req.location_string="";
	}
	$scope.update=function(item)
	{
		$http({
	  	method: 'PUT',
	  	url: 'http://localhost:5000/api/v1/requests/'+item.id,
	 	data: '{"location_string":"'+item.location_string+'","meal_type":"'+item.meal_type+'","meal_time":"'+item.meal_time+'", "longitude":"'+item.longitude+'", "latitude":"'+item.latitude+'", "user_id":"'+JSON.parse(window.localStorage.getItem('user')).id+'"}',
	  	headers: {'Content-type':'application/json', 'Authorization':'Basic '+Base64.encode(JSON.parse(localStorage.getItem("user")).token+':""')}
		}).then(function successCallback(response) {
	    // this callback will be called asynchronously
	    // when the response is available
	    alert("Request updated successfully");
	  	}, function errorCallback(response) {
	  	alert("ERRORS!");
	    // called asynchronously if an error occurs
	    // or server returns response with an error status.
	  });
	}
	$scope.propose=function(item)
	{
		$http({
	  	method: 'POST',
	  	url: 'http://localhost:5000/api/v1/proposals',
	  	data: '{"user_proposed_to":"'+item.user_id+'","user_proposed_from":"'+2+'","request_id":"'+item.id+'"}',
	  	headers: {'Content-type':'application/json', 'Authorization':'Basic '+Base64.encode(JSON.parse(localStorage.getItem("user")).token+':""')}
		}).then(function successCallback(response) {
	    // this callback will be called asynchronously
	    // when the response is available
	    alert("Proposal Sent!");
	    console.log(response);
	  	}, function errorCallback(response) {
	  	alert("ERRORS!");
	    // called asynchronously if an error occurs
	    // or server returns response with an error status.
	  });
	}
	if(window.localStorage && window.localStorage.getItem('user')!==null)
	$http({
	  method: 'GET',
	  url: 'http://localhost:5000/api/v1/requests',
	  headers: {'Authorization':'Basic '+Base64.encode(JSON.parse(localStorage.getItem("user")).token+':""')}
	}).then(function successCallback(response) {
		$scope.myrequests=[];
		$scope.openrequests=[];
	    // this callback will be called asynchronously
	    // when the response is available
	    for(i=0; i<response.data.Requests.length; i++)
	    	if(response.data.Requests[i].user_id==JSON.parse(localStorage.getItem("user")).user)
	    		$scope.myrequests.push(response.data.Requests[i]);
	    	else
	    		$scope.openrequests.push(response.data.Requests[i]);


	  }, function errorCallback(response) {
	  	console.log(response);
	  	if(response.status===401)
	  		$window.location.href = '/';
	  	alert("ERRORS!");
	    // called asynchronously if an error occurs
	    // or server returns response with an error status.
	  });
	
});

app.controller('proposalController', function($scope, $http)
{
	if(window.localStorage && window.localStorage.getItem('user')!==null)
	$http({
	  method: 'GET',
	  url: 'http://localhost:5000/api/v1/proposals',
	  headers: {'Authorization':'Basic '+Base64.encode(JSON.parse(localStorage.getItem("user")).token+':""')}
	}).then(function successCallback(response) {
		$scope.proposalsMade=[];
		$scope.proposalsReceived=[];
	    for(i=0; i<response.data.Proposals.length; i++)
	    	if(response.data.Proposals[i].user_proposed_to==JSON.parse(localStorage.getItem("user")).user&&response.data.Proposals[i].filled!=1)
	    		{$scope.proposalsReceived.push(response.data.Proposals[i]); console.log(response);}
	    	else if(response.data.Proposals[i].user_proposed_from==JSON.parse(localStorage.getItem("user")).user)
	    		$scope.proposalsMade.push(response.data.Proposals[i]);
	  }, function errorCallback(response) {
	  	console.log("ERRORS!");
	  });
	$scope.del=function (item)
	{
		if(window.localStorage && window.localStorage.getItem('user')!==null)
		{
		$http({
		method: 'DELETE',
		url: 'http://localhost:5000/api/v1/proposals/'+item.id,
		headers: {'Content-type':'application/json', 'Authorization':'Basic '+Base64.encode(JSON.parse(localStorage.getItem("user")).token+':""')}
		}).then(function successCallback(response) {
		    var index = $scope.proposalsReceived.indexOf(item);
  			$scope.proposalsReceived.splice(index, 1); 
		  }, function errorCallback(response) 
		  {
		  	console.log(response);
		  });
		}

	};
	$scope.accept=function (item)
	{
		if(window.localStorage && window.localStorage.getItem('user')!==null)
		$http({
	  	method: 'PUT',
	  	url: 'http://localhost:5000/api/v1/proposals/'+item.id,
	 	data: '{"filled":"1"}',
	  	headers: {'Content-type':'application/json','Authorization':'Basic '+Base64.encode(JSON.parse(localStorage.getItem("user")).token+':""')}
		}).then(function successCallback(response) {
	    var index = $scope.proposalsReceived.indexOf(item);
  		$scope.proposalsReceived.splice(index, 1); 
	    console.log(response);
	    alert("Proposal Accepted Successfully!");
	  	}, function errorCallback(response) {
	  	alert("ERRORS!");
	    // called asynchronously if an error occurs
	    // or server returns response with an error status.
	  });
	}
});

app.controller('mealDateController', function($scope, $http)
{
	$scope.message='mealdate';
	$scope.timeConverter=timeConverter;
	
	if(window.localStorage && window.localStorage.getItem('user')!==null)
	$http({
	  method: 'GET',
	  url: 'http://localhost:5000/api/v1/dates',
	  headers: {'Authorization':'Basic '+Base64.encode(JSON.parse(localStorage.getItem("user")).token+':""')}
	}).then(function successCallback(response) {
	    $scope.mealdates=response.data["Meal Dates"];
	  }, function errorCallback(response) {
	  	alert("ERRORS!");
	    // called asynchronously if an error occurs
	    // or server returns response with an error status.
	  });
	$scope.edit=function(item)
	{
		angular.element(document.getElementById("dateForm")).scope().date=item;
	}
	$scope.del=function (item)
	{
		if(window.localStorage && window.localStorage.getItem('user')!==null)
		{
		$http({
		method: 'DELETE',
		url: 'http://localhost:5000/api/v1/dates/'+item.id,
		headers: {'Content-type':'application/json', 'Authorization':'Basic '+Base64.encode(JSON.parse(localStorage.getItem("user")).token+':""')}
		}).then(function successCallback(response) {
		    var index = $scope.mealdates.indexOf(item);
  			$scope.mealdates.splice(index, 1); 
		  }, function errorCallback(response) 
		  {
		  	console.log(response);
		  });
		}
	};

	$scope.update=function(item)
	{
		$http({
	  	method: 'PUT',
	  	url: 'http://localhost:5000/api/v1/dates/'+item.id,
	 	data: '{"restaurant_name":"'+item.restaurant_name+'","restaurant_address":"'+item.restaurant_address+'","meal_time":"'+item.meal_time+'", "restaurant_picture":"'+item.restaurant_picture+'"}',
	  	headers: {'Content-type':'application/json', 'Authorization':'Basic '+Base64.encode(JSON.parse(localStorage.getItem("user")).token+':""')}
		}).then(function successCallback(response) {
	    // this callback will be called asynchronously
	    // when the response is available

	    alert("Date updated successfully");
	  	}, function errorCallback(response) {
	  	alert("ERRORS!");
	    // called asynchronously if an error occurs
	    // or server returns response with an error status.
	  });
	}
});

app.controller('userController', function($scope, $http, $window)
{
	if(window.localStorage && window.localStorage.getItem('user')!==null)
	{
		$window.location.href = '/#/requests';
	}
	else
	{
		$scope.registerUser=function(user)
		{
		$http({
		  method: 'POST',
		  url: 'http://localhost:5000/api/v1/users',
		  data: '{"username":"'+user.username+'","password":"'+user.password+'","email":"'+user.email+'","picture":"'+user.picture+'"}',
		  headers: {'Content-type':'application/json'}
		}).then(function successCallback(response) {

			$http({
	  	method: 'GET',
	  	url: 'http://localhost:5000/token',
	  	headers: {'Authorization':'Basic '+Base64.encode(user.username+':'+user.password)}
		}).then(function successCallback(response) {
	    $scope.hideloginform(response.data.username);
	    localStorage.setItem("user", JSON.stringify(response.data));
	    	$window.location.href = '/#/requests';
	  	}, function errorCallback(response) {
	  	alert("ERRORS!");
	    // called asynchronously if an error occurs
	    // or server returns response with an error status.
	  });


		  }, function errorCallback(response) {
		  	alert("ERRORS!");
		    // called asynchronously if an error occurs
		    // or server returns response with an error status.
		  });
		}
	}
});



