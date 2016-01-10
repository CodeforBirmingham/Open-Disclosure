angular.module('openDisclosure')
  .controller('candidatesCtrl', ['$scope', 'Api', function($scope, Api) {
    $scope.sortFields = [{
      name: 'name',
      label: 'Name'
    }, {
      name: 'office',
      label: 'Office'
    }, {
      name: 'contribution',
      label: 'Total Raised'
    }, {
      name: 'expenditure',
      label: 'Total Spent'
    }];

    $scope.curSortField = 'contribution';
    $scope.curSortOrderDesc = true;
    $scope.setSortField = function(sortField) {
      if ($scope.curSortField === sortField) {
        // Invert order.
        $scope.curSortOrderDesc = !$scope.curSortOrderDesc;
      } else {
        // Change sort field.
        $scope.curSortField = sortField;
        $scope.curSortOrderDesc = false;
      }
    };
    $scope.getOrderBy = function() {
      return $scope.curSortOrderDesc ? '-' + $scope.curSortField : $scope.curSortField;
    };
    $scope.barColor = function(spent) {
      if(spent < 0){
        return 'candidate-bar-negative';
      } else if (spent > 0) {
        return 'candidate-bar-positive';
      } else {
        return 'candidate-bar';
      }
    };
    $scope.initials = function(name, image) {
      if (!image) {
        var initials = name.match(/\b([A-Z])/g).join('').substring(0, 3);
        return initials;
      }
    };

    Api.getCandidates().then(function(candidates) {
      $scope.candidates = candidates;
      console.log($scope.candidates);
    });
  }]);
