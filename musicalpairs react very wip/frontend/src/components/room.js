import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom'


export default function Room(props) {
    const initialState = {
        round_count: 2,
        is_host: false
    }
    const [roomData, setRoomData] = useState(initialState) 
    const { roomCode } = useParams()
  
    useEffect(() => {
      fetch("/audio/get-room" + "?code=" + roomCode)
        .then(res => res.json())
        .then(data => {
          setRoomData({
            roomData, 
            round_count: data.round_count,
            round_list: data.round_list,
            is_host: data.is_host,
          })
        })
    },[roomCode,setRoomData]) //It renders when the object changes .If we use roomData and/or roomCode then it rerenders infinite times
    return (
      <div>
        <h3>{roomCode}</h3>
        {/* <p>Votes: {roomData.votes_to_skip}</p> */}
        <p>RoundCount: {roomData.round_count}</p>
        <p>RoundList: {roomData.round_list}</p>  
        {/* <p>Guest: {roomData.guest_can_pause.toString()}</p> */}
        <p>Host: {roomData.is_host.toString()}</p>
      </div>
    )
  }