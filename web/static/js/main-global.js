window.Vue.options.delimiters = ['[[', ']]'];

window.Vue.config.productionTip = false;

window.Vue.filter('datetime', function (date, dateFormat) {
    let m;
    if (dateFormat == null) {
        dateFormat = "YYYY / MM / DD (dd) HH:mm";
    }
    if (typeof date === 'string' && date.indexOf('T') !== -1 && date.indexOf('Z') === -1) {
        date = date + 'Z';
    }
    window.moment.locale('zh-TW');
    m = moment(date);
    if (m.isValid()) {
        return m.format(dateFormat);
    } else {
        return date;
    }
});
