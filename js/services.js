app.factory('Request', function($resource) {
  return $resource('http://localhost:5000/api/v1/requests/:id', { id: '@_id' }, {
    update: {
      method: 'PUT'
    }
  });
});