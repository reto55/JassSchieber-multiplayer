/*!
 * CSS3 Card Games Example
 * http://gamedesign.cc/html5games/CSS3-matching-game/
 *
 * This is an example game for the book HTML5 Games Development: A Beginning Guide.
 *
 * Copyright 2010, Thomas Seng Hin Mak
 * makzan@gmail.com
 *
 * All Right Reserved.
 */

// a global object to hold all global variables related to the game.
var schieberGame = {};

// all possible values for each card in deck
schieberGame.deck = [
	'cardSEK','cardSIB','cardSIK',
	'cardRU','cardRO','cardRA',
	'cardEB','cardEU', 'cardEO'	
];

// every code inside $(function(){}) will be run
// after the DOM is loaded and ready.
$(function(){
	for(var i=0;i<=7;i++){
		$(".card:first-child").clone().appendTo("#cards");
	}
	// initialize each card
	$("#cards").children().each(function(index) {
		// align the cards to be 4x3 ourselves.
		$(this).css({
			"left" : 40+(80 * index )
		});
		var pattern = schieberGame.deck.pop();
		// visually apply the pattern on the card's back side.
		// the pattern value is actually a CSS class with the
		// corrisponding playing card graphic.
		$(this).find(".back").addClass(pattern);

		// embed the pattern data into the DOM element.
		$(this).attr("data-pattern",pattern);

		// listen the click event on each card DIV element.
		$(this).click(selectCard);
	});
});

function selectCard() {

	// add the class "card-flipped".
	// the browser will animate the styles between current state and card-flipped state.
	$(this).addClass("card-flipped");
}


// a function to delete all removed cards
function removeTookCards()
{
	$(".card-removed").remove();
}

// a function to check if the flipped card match the pattern.
function isMatchPattern()
{
	var cards = $(".card-flipped");
	var pattern = $(cards[0]).data("pattern");
	var anotherPattern = $(cards[1]).data("pattern");
	return (pattern == anotherPattern);
}

