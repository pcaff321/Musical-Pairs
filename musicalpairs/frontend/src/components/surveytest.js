import React, { Component } from "react";

export default class SurveyTest extends Component {
    constructor(props) {
        super(props);
    }

    render() {
        return (
            <audio controls autoPlay>
                <source src="/static/april.mp3" type="audio/mp3" hidden></source>
            </audio>
        )
    }
}