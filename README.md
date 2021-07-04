# TheAlmightyDashboard

This is a lightweight tool to display live quotes from marketwatch, coinmarketcap or get your current balance from your uphold account, coinbase, or local monero wallet.

## Usage

To run the tool execute:
~~~
python dashboard_threaded.py
~~~
to run without any accounts attached and only show some live quotes from marketwatch and coinmarketcap as defined in <tt>config_no_accounts.json</tt>.

If you want to read the balances from your accounts at coinbase or uphold or from a local monero wallet or you just want to read quotes from links you've defined you can edit the file <tt>config_template.json</tt> according to your needs and run as follows:
~~~
python dashboard_threaded.py <path_to_your_config.json>
~~~
