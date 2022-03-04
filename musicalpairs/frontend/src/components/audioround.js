import React, { Component } from "react";

export default class AudioRound extends Component {
    constructor(props) {
        super(props);
    }

    render() {
        return (
            <div>
                <h1> Close your eyes </h1>
                <div class='row'>
                    <audio controls>
                        <source src="https://github.com/Pietro-Rizzo/words_and_nonwords_1/blob/main/delay_music_15_seconds.wav?raw=true" type="audio/wav" />
                        Your browser does not support the audio element.
                    </audio>
                </div>
            </div>
        )
    }
}