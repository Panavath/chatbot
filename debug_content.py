#!/usr/bin/env python3
"""
Debug script to check content in the database
"""

import asyncio
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.database import SessionLocal
from app.database.models.content_model import ContentModel

async def debug_content():
    """Debug content in the database"""
    try:
        db = SessionLocal()
        
        print("=== All Content in Database ===")
        contents = db.query(ContentModel).all()
        print(f"Total content items: {len(contents)}")
        
        for i, content in enumerate(contents, 1):
            print(f"\n{i}. Content Item:")
            print(f"   ID: {content.id}")
            print(f"   Page: '{content.page}'")
            print(f"   Slug: '{content.slug}'")
            print(f"   Name: '{content.name}'")
            print(f"   Khmer Title: '{content.kh_title}'")
            print(f"   English Title: '{content.en_title}'")
            print(f"   Has Khmer Content: {'Yes' if content.kh_content else 'No'}")
            print(f"   Has English Content: {'Yes' if content.en_content else 'No'}")
            if content.kh_content:
                print(f"   Khmer Content Preview: {content.kh_content[:100]}...")
            if content.en_content:
                print(f"   English Content Preview: {content.en_content[:100]}...")
        
        print("\n=== Testing Search Terms ===")
        search_terms = ["pas", "sihanoukville", "port", "autonomous", "ការិយាល័យ", "អគ្គនាយកដ្ឋាន"]
        
        for term in search_terms:
            print(f"\nSearching for '{term}':")
            matching_contents = []
            
            for content in contents:
                # Check if term appears in any field
                if (term.lower() in content.en_title.lower() or 
                    term.lower() in content.kh_title.lower() or
                    term.lower() in content.en_content.lower() or
                    term.lower() in content.kh_content.lower() or
                    term.lower() in content.name.lower() or
                    term.lower() in content.page.lower() or
                    term.lower() in content.slug.lower()):
                    matching_contents.append(content)
            
            print(f"   Found {len(matching_contents)} matches")
            for content in matching_contents:
                print(f"   - ID {content.id}: {content.en_title} (page: {content.page}, slug: {content.slug})")
        
        db.close()
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_content()) 