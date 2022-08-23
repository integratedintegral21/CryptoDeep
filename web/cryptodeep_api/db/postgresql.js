const HOST = 'localhost'
const PORT = 5432
const DB = 'cryptodb'
const USER = 'cryptodb'
const PASSWORD = 'cryptodb'


const pgp = require('pg-promise')(/* options */)
const db = pgp('postgres://' + USER + ':' + PASSWORD + '@' + HOST + ':' + PORT + '/' + DB)

async function get_all_records(crypto, currency) {
    const table_name = crypto + '_' + currency + '_records'
    const records = await db.many('SELECT * FROM ' + table_name)
    return records
}

module.exports.get_all_records = get_all_records
