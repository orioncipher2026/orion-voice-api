const { Vonage } = require('@vonage/server-sdk');
const fs = require('fs');
const path = require('path');

const privateKey = fs.readFileSync(path.join(__dirname, 'private.key'));
const applicationId = '312455f6-4460-49f0-9ce4-5e9238e181cb';

const vonage = new Vonage({
    applicationId: applicationId,
    privateKey: privateKey
});

// NCCO - what happens when Les answers
const ncco = [{
    "action": "talk",
    "text": "Hello Les! This is Orion calling you. Let me connect you to my voice assistant.",
    "voiceName": "Amy"
}, {
    "action": "connect",
    "from": "17806699599",
    "endpoint": [{
        "type": "sip",
        "uri": "sip:+17806699599@sip.rtc.elevenlabs.io:5060;transport=tls"
    }]
}];

vonage.voice.createOutboundCall({
    to: [{ type: 'phone', number: '15198091100' }],
    from: { type: 'phone', number: '17806699599' },
    ncco: ncco
})
.then(resp => console.log('Call initiated!', resp))
.catch(err => console.error('Error:', err));
