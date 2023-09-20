from flask import Flask,render_template,url_for,request,redirect
import json
from requests_oauthlib import OAuth1Session

app=Flask(__name__)

def get_authenticated():
    client = OAuth1Session('###',
                client_secret='###',
                resource_owner_key='###',
                resource_owner_secret='###',
                realm='6420671',
                signature_method="HMAC-SHA256")
    return client

def parser(otherRefNum):
    client = get_authenticated()

    url = "https://6420671.suitetalk.api.netsuite.com/services/rest/query/v1/suiteql?limit=5"

    payload = json.dumps({
    "q": f"SELECT id, custbody_dgt_ns_locked FROM transaction WHERE recordtype='salesorder' AND otherRefNum='#{otherRefNum}'"#CAU1139
    })

    headers = {
    'prefer': 'transient',
    'Content-Type': 'application/json',
    }
    response = client.request("POST", url, headers=headers, data=payload)

    if response.status_code == 200:
        try:
            locked = response.json()['items'][0]['custbody_dgt_ns_locked']
            locked = '<strong><span style="color: #339966;">YES</span></strong> ' if locked == 'F' else '<strong><span style="color: #ff0000;">CAN NOT CANCEL</span></strong>'
            transid = response.json()['items'][0]['id']
        except:
            locked = '<span style="color: #ff0000;">Order Not Found</span>'
            transid ='0'

    PreSale="ERROR"
    if transid !='0':
        payload = json.dumps({
        "q": f"SELECT SIGN(COUNT(Transaction)) as PreSale FROM TransactionLine WHERE ( Transaction ={transid} and CUSTCOL_PRE_SALE = 'T' )'"
        })

        response = client.request("POST", url, headers=headers, data=payload)

        if response.status_code == 200:
            try:
                PreSaleBool = response.json()['items'][0]['presale']
                print(PreSaleBool)
                PreSale="ERROR"
                if PreSaleBool == "0":
                    PreSale="No"
                if PreSaleBool == "1":
                    PreSale = "Yes"
            except:
                PreSale = 'ERROR'

    return locked,PreSale


@app.route('/', methods=['POST','GET'])
def index():

    if request.method == 'POST':
        order_number=request.form['content']
        order_number=order_number.upper()
        locked,PreSale  = parser(order_number)
        return render_template('index.html',OrderNo='Order: '+order_number,locked='Status: '+locked,presale='Presale: '+PreSale)
        #return redirect('/')
    else:
        return render_template('index.html')
