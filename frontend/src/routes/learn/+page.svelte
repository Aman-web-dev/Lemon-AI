<script lang="ts">
	import { io } from 'socket.io-client';
	import { sendMessage } from './functions';
	import { json } from '@sveltejs/kit';
	const incomingMessage = $state([]);
	const outGoingMessage = $state([]);
	const socket = io('http://localhost:9000/');

	
	const sendWsMessage = (type: string, body: any) => {
		socket.emit('chat message', JSON.stringify({ type, body }));
	};

	sendWsMessage("join",{channelName:"channel123",userId:"Frontend"})

	const deviceSetUp = async () => {};

	let localPeerConnection;
	let localStream;

	const createOffer = async () => {
		try {
			console.log('Device Setup is getting Invoked');
			await navigator.mediaDevices
				.getUserMedia({ video: false, audio: true })
				.then((stream) => {
					localStream = stream;
				})
				.catch((error) => {
					console.log(error);
				});
			console.log('Device Setup Completed');
		} catch {
			console.log("Error While getting User's Media device");
		}
		let servers;
		const pcConstraints = {
			optional: [{ DtlsSrtpKeyAgreement: true }]
		};

		localPeerConnection = new RTCPeerConnection(servers, pcConstraints);
		localPeerConnection.onicecandidate = gotLocalIceCandidateOffer;
		localPeerConnection.ontrack = gotRemoteStream;
		localStream.getTracks().forEach((track) => {
			localPeerConnection.addTrack(track, localStream);
		});
		localPeerConnection.createOffer().then(gotLocalDescription);
	};

	const gotLocalDescription = (offer) => {
		console.log('got Local Description Invoked', offer);
		localPeerConnection.setLocalDescription(offer);
	};

	// async function to handle received remote stream
	const gotRemoteStream = (event) => {
		console.log('gotRemoteStream invoked');
		const remotePlayer = document.getElementById('audio-player');
		remotePlayer.srcObject = event.stream[0];
	};
	// async function to handle ice candidates
	const gotLocalIceCandidateOffer = (event) => {
		console.log(
			'gotLocalIceCandidateOffer invoked',
			event.candidate,
			localPeerConnection.localDescription
		);
		// when gathering candidate finished, send complete sdp
		if (!event.candidate) {
			const offer = localPeerConnection.localDescription;
			// send offer sdp to signaling server via websocket
			sendWsMessage('send_offer', {
				channelName: 123456,
				userId: 12992,
				sdp: offer
			});
		}
	};


	socket.on('message', (message: string) => {
		console.log(message);
	});

	const handleMessage = (io: any, messageBody: any) => {
		const parsedBody = JSON.parse(messageBody);
		const body = parsedBody.body;
		const type = parsedBody.type;

		switch (type) {
			case 'joined': {
				console.log('users in this channel', body);
                break;
			}

			case 'offer_sdp_received': {
				const offer = body;
				console.log(offer);
				
				break;
			}

			case 'answer_sdp_received': {
				break;
			}

			case 'ice_candidate_received': {
			}

			default:
				break;
		}
	};

const sendSampleMessage=()=>{
	sendWsMessage("sample_message",{message:"hi backend",userId:"frontend",channelName:"channel123"})
}
</script>

<h1>Hello here you will Learn</h1>

<button on:click={createOffer}>Create Offer</button>

<button on:click={sendSampleMessage}>Send Sample Message</button>


<audio controls id="audio-player" autoplay> </audio>
