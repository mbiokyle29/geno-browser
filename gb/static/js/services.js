(function(){
    'use strict';

    var genoBrowserServices = angular.module('genoBrowserServices', ['ngResource']);

    genoBrowserServices.factory('PlotBounds', function(){
        var bounds = [0,-1];
        return bounds;
    });

    genoBrowserServices.factory('TokenHandler', function() {
        var token = "";

        return {
            get: function() {
                return token;
            },

            set: function(newToken) {
                token = newToken;
            }
        }
    });

    genoBrowserServices.factory('Token', ['$resource',
        function($resource) {
            return $resource('/api/token/', {}, {
                get: {
                    headers: {
                        'Content-Type': 'application/json'
                    }
                }
            });
        }]);

    genoBrowserServices.factory('Users', ['$resource',
      function($resource) {
        return $resource('/api/users/:user_id', {}, {
            update: { method:'PUT' }
        });
      }]);

    genoBrowserServices.factory('Tracks', ['$resource',
      function($resource) {
        return $resource('/api/tracks/:track_id', {}, {
            query: { isArray: false },
            update: { method:'PUT' },
            save: {
                method: 'POST',
                transformRequest: angular.identity,
                headers: {'Content-Type': undefined}
            }
        });
      }]);

    genoBrowserServices.factory('Files', ['$resource',
      function($resource) {
        return $resource('/api/files/:type/:user_id/:file_id', {}, {
            query: { isArray: false },
            update: { method:'PUT' }
        });
      }]);

    genoBrowserServices.factory('Views', ['$resource',
      function($resource) {
        return $resource('/api/views/:user_id/:view_id', {}, {
            query: { isArray: false },
            update: { method:'PUT' }
        });
      }]);

    genoBrowserServices.factory('userService',
      function() {
        return {
          username:'',
          email:'',
          password:''
        };
      });
})();