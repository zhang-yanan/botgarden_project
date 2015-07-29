function enablega(method, id, obj, googleAnalytics) {
    var tracker = '';
    if (googleAnalytics == 1) {
         tracker = 'prodtracker.';
    } else if (googleAnalytics == -1) {
         tracker = 'uitracker.';
    }
    if (typeof obj === undefined) {
         return ga(tracker + method, id);
    } else {
        return ga(tracker + method, id, obj);
    }
}