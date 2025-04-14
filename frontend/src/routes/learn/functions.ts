import type { Socket } from "socket.io-client";


export const sendMessage=(msg: string,socket:Socket)=>{
    console.log("message Sending",msg);
    socket.emit("chat message",msg);
}