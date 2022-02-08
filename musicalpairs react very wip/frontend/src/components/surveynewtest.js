import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom'
import SurveyTest from './surveytest';
// import SurveyTest2 from './surveytest2';

function showNextStage(displayedTable, room_count) {
    let newStage = displayedTable + 1;
    if (newStage > room_count) {
        newStage = room_count;
    }
    return newStage;
}

function showPreviousStage(displayedTable) {
    let newStage = displayedTable - 1;
    if (newStage < 1) {
        newStage = 1;
    }
    return newStage;
}

export default function Survey(props) {
    const initialState = {
        round_count: 0,
        is_host: false
    }
    const [ roomData, setRoomData ] = useState(initialState) 
    const { roomCode } = useParams()
    const [ displayedTable, setDisplayedTable ] = useState(1);
    const [ components, setComponents ] = useState({});
    const [ is_components_set, setIsComponentsSet ] = useState(false)

    function keyEventListener(e) {
        if (e.keyCode == '39') {
            setDisplayedTable(showNextStage(displayedTable, roomData.round_count));
        } else if (e.keyCode == '37') {
            setDisplayedTable(showPreviousStage(displayedTable));
        }
    }

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
        
        window.addEventListener('keydown', keyEventListener);

        // cleanup this component
        return () => {
            window.removeEventListener('keydown', keyEventListener);
        };

    }, [roomCode, setRoomData, roomData.round_count, displayedTable])

    if (roomData.round_count != 0 && is_components_set === false) {
        let initial_components = {};
        for (let i = 1; i < roomData.round_count + 1; i++) {
            initial_components[i] = <div><p>{i}</p> <SurveyTest /></div>
        }
        setIsComponentsSet(true);
        setComponents(initial_components);
    }

    return (
    //   <div>
    //     <h3>{roomCode}</h3>
    //     <p>Votes: {roomData.votes_to_skip}</p>
    //     <p>RoundCount: {roomData.round_count}</p>
    //     <p>RoundList: {roomData.round_list}</p>  
    //     <p>Guest: {roomData.guest_can_pause.toString()}</p>
    //     <p>Host: {roomData.is_host.toString()}</p>
    //   </div>
        <div>
            {components[displayedTable]}
        </div>
    )
  }