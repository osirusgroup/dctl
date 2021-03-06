const program = require('commander');
const util = require('./util');

program
  .description('Delete a Transaction Type')
  .arguments('<transactionTypes...>')
  .option('-v, --verbose', '(optional) Enable STDOUT logger in your Dragonchain SDK')
  .option('-i, --dragonchainId [dragonchainID]', '(optional) Override the default dragonchain ID for this command')
  .parse(process.argv);

util.wrapper(program, async client => {
  const results = [];
  await Promise.all(
    program.args.map(async transactionType => {
      results.push(
        await client.deleteTransactionType({
          transactionType
        })
      );
    })
  );
  console.log(JSON.stringify(results, null, 2));
});
