function createDateAsUTC(date) {
    return new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate(), date.getHours(), date.getMinutes(),
        date.getSeconds()));
}

module.exports.createDateAsUTC = createDateAsUTC;
