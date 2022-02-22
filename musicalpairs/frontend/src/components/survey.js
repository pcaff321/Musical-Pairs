import React, { Component } from "react";
import SurveyTest from "./surveytest";
import SurveyTest2 from "./surveytest2";

export default class Survey extends Component {
    constructor(props) {
        super(props);
        this.components = {
            1: <SurveyTest />,
            2: <SurveyTest2 />
        }
        this.stageCount = 2;
        this.state = {displayedTable: 1}
        window.addEventListener('keydown', (e) => {
            if (e.keyCode == '39') {
                this.showNextStage();
            } else if (e.keyCode == '37') {
                this.showPreviousStage();
            }
        });
    }

    showNextStage = () => {
        let newStage = this.state.displayedTable + 1;
        if (newStage > this.stageCount) {
            newStage = stageCount;
        }
        this.setState({displayedTable: newStage});
    }

    showPreviousStage = () => {
        let newStage = this.state.displayedTable - 1;
        if (newStage < 1) {
            newStage = 1;
        }
        this.setState({displayedTable: newStage});
    }

    render() {
        return(
            <div>
                {this.components[this.state.displayedTable]}
            </div>
        )
    }
}