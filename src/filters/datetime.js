import moment from 'moment';

const datetime = (date, dateFormat, locale = "zh-TW") => {
    let m;
    if (dateFormat == null) {
        dateFormat = "YYYY / MM / DD (dd) HH:mm";
    }
    if (typeof date === 'string' && date.indexOf('T') !== -1 && date.indexOf('Z') === -1) {
        date = date + 'Z';
    }
    moment.locale(locale);
    m = moment(date);
    if (m.isValid()) {
        return m.format(dateFormat);
    } else {
        return date;
    }
};

export {datetime};
