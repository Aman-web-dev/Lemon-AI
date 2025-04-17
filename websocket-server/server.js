import express from "express";
import "dotenv/config";
import { Server } from "socket.io";
import { createServer } from "http";
import cors from "cors";

const PORT = process.env.PORT || 7000;
const app = express();

const httpServer = createServer(app);

const channels = {};

app.use(cors({ origin: "*", methods: ["GET", "POST", "PUT", "DELETE"] }));

app.use(express.json());
app.get("/", (req, res) => {
  res.send("Hello World");
});

const io = new Server(httpServer, {
  cors: {
    origin: "*",
    methods: ["GET", "POST", "PUT", "DELETE"],
    credentials: true,
  },
});

io.on("connection", (socket) => {
  console.log("Someone Connected");

  socket.emit("message", "Hi There!");
  socket.on("chat message", (message) => {
    onMessage(socket, message);
    socket.emit("message", "Hi Again!");
    console.log(message);
  });
  socket.on("disconnect", () => {
    console.log("Someone is Disconnected");
    onClose(socket);
  });
});

const send = (socket, type, body) => {
  console.log("sending",type,body);
  console.log(channels);
  socket.send(
    "message",
    JSON.stringify({
      type,
      body,
    })
  );
};

const clearClient = (socket) => {
  Object.keys(channels).forEach((channelName) => {
    Object.keys(channelName).forEach((uid) => {
      if (channels[channelName][uid] === socket) {
        delete channels[channelName][uid];
      }
    });
  });
  console.log(channels);
};

const onMessage = (socket, message) => {
  console.log("Channels",channels)
  const parsedMessage = JSON.parse(message);
  const type = parsedMessage.type;
  const body = parsedMessage.body;
  const channelName = body.channelName;
  const userId = body.userId;

  switch (type) {
    case "join": {
      if (
        channels[channelName] &&
        Object.keys(channels[channelName]).length < 2
      ) {
        channels[channelName][userId] = socket;
      } else {
        channels[channelName] = {};
        channels[channelName][userId] = socket;
      }
      const userIds = channelName[channelName];
      send(socket, "joined", userIds);
      break;
    }

    case "quit": {
      if (channels[channelName][userId]) {
        channels[channelName][userId] = null;
        const usersInChannel = Object.keys(channels[channelName]).length;
        if (usersInChannel == 0) {
          delete channels[channelName];
        }
      }

      break;
    }

    case "send_offer": {
      const sdp = body.sdp;
      if (channels[channelName]) {
        Object.keys(channels[channelName]).forEach((user) => {
          if (user.toString() !== userId.toString()) {
            send(channels[channelName][user], "offer_sdp_received", sdp);
          }
        });
      }
      break;
    }

    case "send_answer": {
      const sdp = body.sdp;
      if (channels[channelName]) {
        Object.keys(channels[channelName]).forEach((user) => {
          if (user.toString() !== userId.toString()) {
            send(channels[channelName][userId], "answer_sdp_received", sdp);
          }
        });
      }
      break;
    }

    case "send_ice_candidate": {
      const candidate = body.candidate;
      if (channels[channelName]) {
        Object.keys(channels[channelName]).forEach((user) => {
          if (user.toString() !== userId.toString()) {
            send(
              channels[channelName][user],
              "ice_candidate_received",
              candidate
            );
          }
        });
      }
      break;
    }

    case "sample_message":{
      const message=body.message;
      console.log("sample Message From Frontend")
      if(channels[channelName]){
        console.log("sample Message From Frontend")
        Object.keys(channels[channelName]).forEach((user)=>{
          console.log(user)
          if(user.toString()!=userId.toString()){
            console.log(user)
            send(channels[channelName][user],"sample_message_recieved",{message})
          }
        })
      }
      break;
    }

    default:
      break;
  }

  console.log(body, type, parsedMessage);
};


const onClose = (socket) => {
  clearClient(socket);
};


httpServer.listen(PORT, () => {
  console.log("APP is Running on Port", PORT);
});
