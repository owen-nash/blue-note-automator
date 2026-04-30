import musicbrainzngs
import os

# Set a proper user agent for MusicBrainz
musicbrainzngs.set_useragent("BlueNoteAutomator", "0.1", "https://github.com/ownash")

def get_album_personnel(artist_name, album_name):
    """
    Fetches personnel/credits for a given album using MusicBrainz.
    """
    try:
        # Search for the release
        result = musicbrainzngs.search_releases(artist=artist_name, release=album_name, limit=1)
        
        if not result['release-list']:
            return "Personnel data not found on MusicBrainz."
        
        release_id = result['release-list'][0]['id']
        
        # Get detailed release info including artist relations (personnel)
        # We fetch 'artist-rels' and 'work-rels' to get performers
        release = musicbrainzngs.get_release_by_id(release_id, includes=["artist-rels", "recordings", "recording-level-rels"])
        
        personnel = []
        
        # Check for relations at the release level
        if 'artist-relation-list' in release['release']:
            for rel in release['release']['artist-relation-list']:
                name = rel['artist']['name']
                role = rel.get('type', 'performer')
                personnel.append(f"{name} ({role})")
        
        # If no release-level relations, we could check recordings, but let's keep it simple for now
        if not personnel:
            return "No specific personnel listed at release level."
            
        return ", ".join(personnel)
        
    except Exception as e:
        return f"Error fetching metadata: {str(e)}"

if __name__ == "__main__":
    # Test with a known Jazz classic
    test_artist = "Miles Davis"
    test_album = "Kind of Blue"
    print(f"Fetching personnel for {test_artist} - {test_album}...")
    print(get_album_personnel(test_artist, test_album))
