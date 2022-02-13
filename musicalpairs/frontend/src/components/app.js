import React, { Component } from "react";
import { render } from "react-dom";
import HomePage from "./homepage";
import CreateSurvey from "./createsurvey";
import JoinSurvey from "./joinsurvey";
import SurveyTest from "./surveytest";
import SurveyTest2 from "./surveytest2";
import Survey from "./surveynewtest"
import Room from "./room"
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";


export default class App extends Component {
    constructor(props) {
        super(props);
    }

    render() {
        return (
            <Router>
                <Routes>
                    <Route exact path="/" element={ <HomePage /> }></Route>
                    {/* <Route exact path="/survey" element={ <SurveyTest /> }></Route>
                    <Route exact path="/survey2" element={ <SurveyTest2 /> }></Route> */}
                    <Route exact path="/survey/:roomCode" element={ <Survey /> }></Route>
                    <Route exact path="/create" element={ <CreateSurvey /> }></Route>
                    <Route exact path="/join" element={ <JoinSurvey /> }></Route>
                    <Route exact path="/room/:roomCode" element={ <Room /> }></Route>
                </Routes>
            </Router>
        );
    }
}

const appDiv = document.getElementById("app");
render(<App />, appDiv);