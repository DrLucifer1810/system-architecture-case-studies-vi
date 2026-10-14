package matchmaker

import (
	"errors"
)

type Contestant struct {
	ID    int64
	Seed  int
	Name  string
	Score float64
}

type MatchPair struct {
	MatchID int64
	Round   int
	Player1 Contestant
	Player2 Contestant
}

// GenerateKnockoutRound generates standard seeded 1v1 pairings for a knockout stage.
// Contestant with Seed i is paired against Contestant with Seed (N - i + 1).
func GenerateKnockoutRound(contestants []Contestant, round int) ([]MatchPair, error) {
	n := len(contestants)
	if n < 2 || n%2 != 0 {
		return nil, errors.New("contestant count must be an even number >= 2")
	}

	matches := make([]MatchPair, 0, n/2)
	for i := 0; i < n/2; i++ {
		p1 := contestants[i]
		p2 := contestants[n-1-i]

		matches = append(matches, MatchPair{
			MatchID: int64(i + 1),
			Round:   round,
			Player1: p1,
			Player2: p2,
		})
	}

	return matches, nil
}
