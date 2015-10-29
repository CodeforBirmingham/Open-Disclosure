angular.module('openDisclosure').factory('Api', ['$http', '$q', function ($http, $q) {

    var endpoint, datasets, Api;

    endpoint = "https://brigades.opendatanetwork.com/resource/";

    datasets = {
        parties: "kjgr-g56d",
        transactions: "vcap-yyfq",
        transactees: "9xmj-xdkh",
        districts: "p8kt-epji"
    };

    Api = {};

    Api.getCandidates = function () {
        var partiesQuery, transactionsQuery;
        partiesQuery = 'type=Candidate&status=Active';
        transactionsQuery = '$select=party_id,type,sum(amount)&$group=party_id,type';
        return $q.all([
            $http.get(endpoint + datasets.parties + '.json?' + partiesQuery),
            $http.get(endpoint + datasets.transactions + '.json?' + transactionsQuery)
        ]).then(function (results) {
            var parties, transactions, transactionsIndex;
            parties = results[0].data;
            transactions = results[1].data;
            // Index transactions.
            transactionsIndex = {};
            transactions.forEach(function (x) {
                if (transactionsIndex.hasOwnProperty(x.party_id) === false) {
                    transactionsIndex[x.party_id] = {
                        contribution: 0,
                        expenditure: 0,
                        receipt: 0,
                        inkindcontribution: 0
                    };
                }
                transactionsIndex[x.party_id][x.type.toLowerCase()] += parseFloat(x.sum_amount);
            });
            // Add aggregated information to parties.
            parties = parties.filter(function (x) {
                // Filter out parties that do not have any transactions.
                // Probably not the right thing to do.
                return transactionsIndex.hasOwnProperty(x.id);
            }).map(function (x) {
                var spent;
                var indexEntry;
                indexEntry = transactionsIndex[x.id];
                x.contribution = indexEntry.contribution;
                x.expenditure = indexEntry.expenditure;
                x.spent = (indexEntry.contribution - indexEntry.expenditure) / indexEntry.contribution * 100;
                if (indexEntry.contribution === 0 || indexEntry.expenditure === 0) {
                  x.spent = 0;
                }
                return x;
            });
            return parties;
        });
    };
    return Api;

}]);