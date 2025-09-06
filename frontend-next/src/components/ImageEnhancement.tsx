import React, { useState, useEffect, useRef } from 'react';
import './ImageEnhancement.css';
import { imageEnhancementAPI } from '../services/api';

const ImageEnhancement = () => {
  const [selectedImage, setSelectedImage] = useState(null);
  const [originalImage, setOriginalImage] = useState(null);
  const [enhancedImage, setEnhancedImage] = useState(null);
  const [imageGallery, setImageGallery] = useState([]);
  const [loading, setLoading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [generatedContent, setGeneratedContent] = useState(null);
  const [contentLoading, setContentLoading] = useState(false);
  const [selectedContentTypes, setSelectedContentTypes] = useState({
    facebook: true,
    instagram: true,
    tiktok: false,
    promotional_content: true,
    menu_description: false,
    email_campaign: false,
    google_ads: false,
    social_media_story: false,
    sms_campaign: false
  });
  const [dragActive, setDragActive] = useState(false);
  const [zoomLevel, setZoomLevel] = useState(1);
  const [showBeforeAfter, setShowBeforeAfter] = useState(false);
  
  // New state for enhanced UX features
  const [editableContent, setEditableContent] = useState({});
  const [refreshingContent, setRefreshingContent] = useState({});
  const [hashtagFeedback, setHashtagFeedback] = useState('');
  
  // Enhancement controls
  const [enhancementSettings, setEnhancementSettings] = useState({
    brightness: 0,
    contrast: 0,
    saturation: 0,
    sharpness: 0,
    food_styling: 0
  });

  // New state for prompt-based enhancement
  const [enhancementPrompt, setEnhancementPrompt] = useState('');
  const [selectedPreset, setSelectedPreset] = useState('');
  
  // State for collapsible categories - all collapsed by default
  const [expandedCategories, setExpandedCategories] = useState({});

  const fileInputRef = useRef(null);
  const dropZoneRef = useRef(null);

  // Enhanced preset system organized by categories with collapsible structure
  const enhancementPresets = {
    'Quick & Easy': {
      icon: '⚡',
      description: 'Simple one-click improvements',
      presets: [
        {
          id: 'food_photography',
          name: 'Food Photography Pro',
          description: 'Perfect for restaurant dishes - enhances colors, contrast, and appetite appeal',
          prompt: 'Enhance this food image for professional restaurant marketing with vibrant colors, perfect lighting, and appetizing appeal',
          settings: { brightness: 15, contrast: 25, saturation: 20, sharpness: 15, food_styling: 30 },
          icon: '📸'
        },
        {
          id: 'social_media',
          name: 'Social Media Ready',
          description: 'Optimized for Instagram and Facebook posts with eye-catching vibrancy',
          prompt: 'Make this image pop for social media with enhanced vibrancy, perfect contrast, and Instagram-worthy appeal',
          settings: { brightness: 10, contrast: 30, saturation: 25, sharpness: 10, food_styling: 20 },
          icon: '📱'
        },
        {
          id: 'menu_photo',
          name: 'Menu Photo Perfect',
          description: 'Clean, professional look ideal for menu displays and print materials',
          prompt: 'Create a clean, professional menu photo with balanced lighting, natural colors, and crisp details',
          settings: { brightness: 5, contrast: 15, saturation: 10, sharpness: 20, food_styling: 15 },
          icon: '📋'
        }
      ]
    },
    'AI-Powered Smart': {
      icon: '🤖',
      description: 'Intelligent AI-driven enhancements',
      presets: [
        {
          id: 'make_juicier',
          name: 'Make It Juicier',
          description: 'AI detects burgers, steaks, and meat dishes to enhance juiciness and texture',
          prompt: 'Analyze this food image and if it contains meat, burgers, or steaks, enhance the juiciness, make the patty look bigger and more appetizing, add glistening effects to show moisture and freshness',
          settings: { brightness: 12, contrast: 20, saturation: 25, sharpness: 18, food_styling: 35 },
          icon: '🍔'
        },
        {
          id: 'steam_effect',
          name: 'Add Steam & Heat',
          description: 'Perfect for hot dishes, coffee, soups - adds visual heat effects',
          prompt: 'Add subtle steam effects and heat visualization to make this hot food or beverage look freshly prepared and steaming hot, enhance warmth tones',
          settings: { brightness: 15, contrast: 15, saturation: 20, sharpness: 10, food_styling: 30 },
          icon: '☕'
        },
        {
          id: 'crispy_golden',
          name: 'Golden & Crispy',
          description: 'Enhances fried foods, fries, chicken to look perfectly golden and crispy',
          prompt: 'Enhance the golden color and crispy texture of fried foods, make fries look perfectly golden, chicken look crispy, add appealing texture details',
          settings: { brightness: 18, contrast: 25, saturation: 30, sharpness: 25, food_styling: 40 },
          icon: '🍟'
        },
        {
          id: 'fresh_greens',
          name: 'Fresh & Vibrant',
          description: 'AI-enhanced for salads and fresh ingredients to look crisp and healthy',
          prompt: 'Enhance the freshness of salads and vegetables, make greens look crisp and vibrant, enhance natural colors while maintaining realistic appearance',
          settings: { brightness: 10, contrast: 20, saturation: 35, sharpness: 20, food_styling: 25 },
          icon: '🥗'
        }
      ]
    },
    'Professional Styling': {
      icon: '📸',
      description: 'Professional-grade photo styling',
      presets: [
        {
          id: 'clean_background',
          name: 'Clean White Background',
          description: 'Removes distracting backgrounds and creates a clean, professional look',
          prompt: 'Remove the background and replace with a clean white background, enhance the food item to stand out professionally, perfect for menus and catalogs',
          settings: { brightness: 20, contrast: 25, saturation: 15, sharpness: 20, food_styling: 20 },
          icon: '🎨'
        },
        {
          id: 'fine_dining',
          name: 'Fine Dining Elegance',
          description: 'Sophisticated enhancement for upscale restaurant presentations',
          prompt: 'Enhance with fine dining elegance - sophisticated lighting, refined colors, premium presentation, and elegant atmosphere',
          settings: { brightness: 8, contrast: 20, saturation: 12, sharpness: 18, food_styling: 22 },
          icon: '🍽️'
        },
        {
          id: 'modern_minimal',
          name: 'Modern Minimal',
          description: 'Clean, modern aesthetic perfect for contemporary restaurants',
          prompt: 'Create a modern, minimal aesthetic with clean lines, contemporary lighting, and sophisticated simplicity',
          settings: { brightness: 12, contrast: 22, saturation: 8, sharpness: 25, food_styling: 15 },
          icon: '⚡'
        }
      ]
    },
    'Creative Effects': {
      icon: '🎨',
      description: 'Artistic filters and creative styles',
      presets: [
        {
          id: 'glow_effect',
          name: 'Magical Glow',
          description: 'Adds a subtle magical glow effect to make food look irresistible',
          prompt: 'Add a subtle, magical glow effect around the food to make it look irresistible and special, enhance appeal without looking artificial',
          settings: { brightness: 20, contrast: 18, saturation: 25, sharpness: 15, food_styling: 35 },
          icon: '✨'
        },
        {
          id: 'vintage_filter',
          name: 'Vintage Appeal',
          description: 'Classic vintage look perfect for traditional or heritage restaurants',
          prompt: 'Apply a subtle vintage filter with warm tones, classic appeal, and timeless restaurant atmosphere',
          settings: { brightness: 5, contrast: 15, saturation: 10, sharpness: 8, food_styling: 20 },
          icon: '📷'
        },
        {
          id: 'dramatic_lighting',
          name: 'Dramatic Lighting',
          description: 'Bold, dramatic lighting effects for standout marketing images',
          prompt: 'Create dramatic lighting effects with bold shadows and highlights to make the food the star of the image',
          settings: { brightness: 10, contrast: 35, saturation: 20, sharpness: 20, food_styling: 30 },
          icon: '🎭'
        }
      ]
    }
  };

  // Flatten all presets for backward compatibility
  const allPresets = Object.values(enhancementPresets).flatMap(category => category.presets);

  // Load user's image gallery on component mount
  useEffect(() => {
    loadImageGallery();
  }, []);

  // Toggle category expansion
  const toggleCategory = (categoryName) => {
    setExpandedCategories(prev => ({
      ...prev,
      [categoryName]: !prev[categoryName]
    }));
  };

  // Handle keyboard navigation for category headers
  const handleCategoryKeyPress = (event, categoryName) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      toggleCategory(categoryName);
    }
  };

  const loadImageGallery = async () => {
    try {
      const result = await imageEnhancementAPI.getImages();
      if (result.success) {
        setImageGallery(result.data.images || []);
      }
    } catch (error) {
      console.error('Failed to load image gallery:', error);
    }
  };

  // Handle drag and drop
  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  };

  const handleFileSelect = (file) => {
    console.log('File selected:', file.name, file.type, file.size);
    
    // Validate file type
    if (!file.type.match(/^image\/(jpeg|jpg|png)$/)) {
      alert('Please select a JPEG or PNG image file.');
      return;
    }

    // Validate file size (10MB max)
    if (file.size > 10 * 1024 * 1024) {
      alert('File size must be less than 10MB.');
      return;
    }

    console.log('File validation passed, setting selectedImage');
    setSelectedImage(file);
    
    // Create preview URL immediately
    const reader = new FileReader();
    reader.onload = (e) => {
      console.log('Image loaded, setting originalImage:', e.target.result ? 'Data URL created' : 'No data');
      const imageUrl = e.target.result;
      setOriginalImage(imageUrl);
      setEnhancedImage(null);
      setGeneratedContent(null);
      setShowBeforeAfter(false);
      // Reset enhancement settings
      setEnhancementSettings({
        brightness: 0,
        contrast: 0,
        saturation: 0,
        sharpness: 0,
        food_styling: 0
      });
      
      // Force a re-render to ensure the preview sections appear
      console.log('Original image set, should show preview sections now');
    };
    reader.readAsDataURL(file);
  };

  const handleFileInputChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFileSelect(e.target.files[0]);
    }
  };

  const handleEnhancementChange = (setting, value) => {
    setEnhancementSettings(prev => ({
      ...prev,
      [setting]: value
    }));
  };

  const handlePresetSelection = (preset) => {
    setSelectedPreset(preset.id);
    setEnhancementPrompt(preset.prompt);
    setEnhancementSettings(preset.settings);
  };

  const handlePromptChange = (prompt) => {
    setEnhancementPrompt(prompt);
    setSelectedPreset(''); // Clear preset selection when custom prompt is entered
  };

  const enhanceImage = async (useQuickDefaults = false, usePrompt = false) => {
    if (!selectedImage) {
      console.log('No selected image, cannot enhance');
      return;
    }

    console.log('Starting real image enhancement process...');
    setLoading(true);
    setUploadProgress(0);

    try {
      // Create FormData for the API request
      const formData = new FormData();
      formData.append('file', selectedImage);
      
      // Use either quick defaults, prompt-based settings, or current slider settings
      let settings = enhancementSettings;
      let promptToSend = '';
      
      if (useQuickDefaults) {
        // Apply optimal defaults for food photography
        settings = {
          brightness: 10,    // +10% brightness
          contrast: 20,      // +20% contrast
          saturation: 15,    // +15% saturation
          sharpness: 10,     // +10% sharpness
          food_styling: 25   // Enable food styling
        };
        
        // Update the UI sliders to show the applied settings
        setEnhancementSettings(settings);
        console.log('Applied quick enhancement defaults:', settings);
      } else if (usePrompt && enhancementPrompt.trim()) {
        // Use prompt-based enhancement
        promptToSend = enhancementPrompt.trim();
        console.log('Using prompt-based enhancement:', promptToSend);
      }
      
      // Convert slider values (-100 to 100) to enhancement multipliers (0.5 to 2.0)
      const brightnessMultiplier = 1 + (settings.brightness / 100);
      const contrastMultiplier = 1 + (settings.contrast / 100);
      const saturationMultiplier = 1 + (settings.saturation / 100);
      const sharpnessMultiplier = 1 + (settings.sharpness / 100);
      const foodStylingEnabled = settings.food_styling > 0;
      
      formData.append('brightness', brightnessMultiplier.toString());
      formData.append('contrast', contrastMultiplier.toString());
      formData.append('saturation', saturationMultiplier.toString());
      formData.append('sharpness', sharpnessMultiplier.toString());
      formData.append('food_styling_optimization', foodStylingEnabled.toString());
      
      // Add prompt if provided
      if (promptToSend) {
        formData.append('enhancement_prompt', promptToSend);
      }

      console.log('Enhancement settings:', {
        brightness: brightnessMultiplier,
        contrast: contrastMultiplier,
        saturation: saturationMultiplier,
        sharpness: sharpnessMultiplier,
        food_styling_optimization: foodStylingEnabled
      });

      // Call the real API with progress tracking
      console.log('Calling imageEnhancementAPI.enhanceImage with FormData...');
      console.log('FormData contents:');
      for (let [key, value] of formData.entries()) {
        console.log(`${key}:`, value);
      }
      
      const result = await imageEnhancementAPI.enhanceImage(formData, (progress) => {
        console.log('Upload progress:', progress);
        setUploadProgress(progress);
      });
      
      console.log('API call completed, result:', result);

      if (result.success) {
        console.log('Image enhancement completed successfully:', result.data);
        
        // Set the enhanced image URL from the API response
        const enhancedImageUrl = result.data.enhanced_image || result.data.enhanced_url || result.data.enhanced_image_url;
        if (enhancedImageUrl) {
          setEnhancedImage(enhancedImageUrl);
          setShowBeforeAfter(true);
          
          // Reload the image gallery to show the new enhanced image
          await loadImageGallery();
        } else {
          console.error('Enhanced image URL not found in response. Available keys:', Object.keys(result.data));
          throw new Error('Enhanced image URL not found in response');
        }
      } else {
        throw new Error(result.error || 'Enhancement failed');
      }
      
    } catch (error) {
      console.error('Enhancement failed:', error);
      const errorMessage = error.message || 'Image enhancement failed. Please try again.';
      alert(errorMessage);
    } finally {
      setLoading(false);
      setUploadProgress(0);
    }
  };

  const handleContentTypeChange = (contentType) => {
    setSelectedContentTypes(prev => ({
      ...prev,
      [contentType]: !prev[contentType]
    }));
  };

  const generateContent = async () => {
    if (!enhancedImage && !originalImage) {
      alert('Please upload an image first.');
      return;
    }

    // Check if at least one content type is selected
    const selectedTypes = Object.entries(selectedContentTypes)
      .filter(([_, isSelected]) => isSelected)
      .map(([type, _]) => type);

    if (selectedTypes.length === 0) {
      alert('Please select at least one content type to generate.');
      return;
    }

    setContentLoading(true);

    try {
      // Reload the image gallery to get the latest images
      await loadImageGallery();
      
      // Find the most recent enhanced image from the gallery to get its ID
      let imageId = null;
      if (imageGallery.length > 0) {
        // Use the most recent image (first in the array)
        const latestImage = imageGallery[0];
        imageId = latestImage.id || latestImage.image_id;
        console.log('Found image in gallery:', latestImage);
        console.log('Using image ID:', imageId);
      }

      // Map frontend content types to backend content types
      const contentTypeMapping = {
        facebook: 'social_media_caption',
        instagram: 'social_media_caption',
        tiktok: 'social_media_caption',
        promotional_content: 'promotional_content',
        menu_description: 'menu_description',
        email_campaign: 'email_marketing',
        google_ads: 'promotional_content',
        social_media_story: 'social_media_caption',
        sms_campaign: 'sms_marketing'
      };

      const backendContentTypes = selectedTypes.map(type =>
        contentTypeMapping[type] || 'social_media_caption'
      );

      // If we still don't have an image ID, try to use any enhanced image that was just processed
      if (!imageId && enhancedImage) {
        console.log('No image ID from gallery, but we have an enhanced image. Trying to call API anyway...');
        
        // Try calling the API without image_id - the backend might be able to use the most recent image
        const requestData = {
          content_types: backendContentTypes,
          selected_platforms: selectedTypes
        };

        console.log('Sending content generation request without image_id:', requestData);

        try {
          const result = await imageEnhancementAPI.generateContent(requestData);
          
          if (result.success) {
            console.log('Content generation completed successfully:', result.data);
            
            // Transform the API response to match the expected format
            const generatedContent = result.data.generated_content || {};
            
            const transformedContent = {
              captions: [
                generatedContent.social_media_caption || "Fresh, delicious food made with love and the finest ingredients.",
                generatedContent.menu_description || "Experience authentic flavors that will transport your taste buds.",
                "Perfect for sharing with friends and family!"
              ],
              promotional_content: [
                {
                  type: "Social Media Post",
                  text: generatedContent.promotional_content || "🍽️ Craving something delicious? Come taste the difference at our restaurant! Fresh ingredients, authentic flavors, unforgettable experience. Order now!"
                },
                {
                  type: "Menu Description",
                  text: generatedContent.menu_description || "Made with premium ingredients and traditional techniques for an authentic dining experience."
                },
                {
                  type: "Instagram Story",
                  text: generatedContent.social_media_caption || "Behind the scenes: Watch our chefs create culinary magic! ✨ Swipe up to order yours now!"
                }
              ],
              hashtags: generatedContent.hashtags || [
                "FreshIngredients",
                "AuthenticFlavors",
                "FoodieLife",
                "DeliciousFood",
                "RestaurantLife",
                "FoodLovers",
                "QualityFood",
                "TasteTheDifference"
              ]
            };
            
            setGeneratedContent(transformedContent);
            return;
          }
        } catch (apiError) {
          console.log('API call without image_id failed, falling back to generic content:', apiError);
        }
      }

      if (!imageId) {
        console.log('No enhanced image found, generating general marketing content');
        
        // Generate content without specific image
        const fallbackContent = {
          captions: [
            "Fresh, delicious food made with love and the finest ingredients.",
            "Experience authentic flavors that will transport your taste buds.",
            "Perfect for sharing with friends and family!"
          ],
          promotional_content: [
            {
              type: "Social Media Post",
              text: "🍽️ Craving something delicious? Come taste the difference at our restaurant! Fresh ingredients, authentic flavors, unforgettable experience. Order now!"
            },
            {
              type: "Menu Description",
              text: "Made with premium ingredients and traditional techniques for an authentic dining experience."
            },
            {
              type: "Instagram Story",
              text: "Behind the scenes: Watch our chefs create culinary magic! ✨ Swipe up to order yours now!"
            }
          ],
          hashtags: [
            "FreshIngredients",
            "AuthenticFlavors",
            "FoodieLife",
            "DeliciousFood",
            "RestaurantLife",
            "FoodLovers",
            "QualityFood",
            "TasteTheDifference"
          ]
        };
        
        setGeneratedContent(fallbackContent);
        return;
      }

      console.log('Generating content for image ID:', imageId);

      // Create the request data for content generation matching the backend model
      const requestData = {
        image_id: imageId,
        content_types: backendContentTypes,
        selected_platforms: selectedTypes
      };

      console.log('Sending content generation request:', requestData);

      // Call the real API for content generation
      const result = await imageEnhancementAPI.generateContent(requestData);

      if (result.success) {
        console.log('Content generation completed successfully:', result.data);
        
        // Transform the API response to match the expected format
        const generatedContent = result.data.generated_content || {};
        
        const transformedContent = {
          captions: [
            generatedContent.social_media_caption || "Fresh, delicious food made with love and the finest ingredients.",
            generatedContent.menu_description || "Experience authentic flavors that will transport your taste buds.",
            "Perfect for sharing with friends and family!"
          ],
          promotional_content: [
            {
              type: "Social Media Post",
              text: generatedContent.promotional_content || "🍽️ Craving something delicious? Come taste the difference at our restaurant! Fresh ingredients, authentic flavors, unforgettable experience. Order now!"
            },
            {
              type: "Menu Description",
              text: generatedContent.menu_description || "Made with premium ingredients and traditional techniques for an authentic dining experience."
            },
            {
              type: "Instagram Story",
              text: generatedContent.social_media_caption || "Behind the scenes: Watch our chefs create culinary magic! ✨ Swipe up to order yours now!"
            }
          ],
          hashtags: generatedContent.hashtags || [
            "FreshIngredients",
            "AuthenticFlavors",
            "FoodieLife",
            "DeliciousFood",
            "RestaurantLife",
            "FoodLovers",
            "QualityFood",
            "TasteTheDifference"
          ]
        };
        
        setGeneratedContent(transformedContent);
      } else {
        throw new Error(result.error || 'Content generation failed');
      }
      
    } catch (error) {
      console.error('Content generation failed:', error);
      const errorMessage = error.message || 'Content generation failed. Please try again.';
      alert(errorMessage);
    } finally {
      setContentLoading(false);
    }
  };

  // New function to refresh specific content type
  const refreshContent = async (contentType) => {
    if (!enhancedImage && !originalImage) {
      alert('Please upload an image first.');
      return;
    }

    setRefreshingContent(prev => ({ ...prev, [contentType]: true }));

    try {
      // Reload the image gallery to get the latest images
      await loadImageGallery();
      
      // Find the most recent enhanced image from the gallery to get its ID
      let imageId = null;
      if (imageGallery.length > 0) {
        const latestImage = imageGallery[0];
        imageId = latestImage.id || latestImage.image_id;
      }

      // Map frontend content types to backend content types
      const contentTypeMapping = {
        facebook: 'social_media_caption',
        instagram: 'social_media_caption',
        tiktok: 'social_media_caption',
        promotional_content: 'promotional_content',
        menu_description: 'menu_description',
        email_campaign: 'email_marketing',
        google_ads: 'promotional_content',
        social_media_story: 'social_media_caption',
        sms_campaign: 'sms_marketing'
      };

      const backendContentType = contentTypeMapping[contentType] || 'social_media_caption';

      // Create the request data for content generation
      const requestData = {
        image_id: imageId,
        content_types: [backendContentType],
        selected_platforms: [contentType]
      };

      // Call the API for content generation
      const result = await imageEnhancementAPI.generateContent(requestData);

      if (result.success) {
        const newGeneratedContent = result.data.generated_content || {};
        
        // Update only the specific content type in the existing generated content
        setGeneratedContent(prev => {
          if (!prev) return null;
          
          const updated = { ...prev };
          
          // Update specific content based on type
          if (contentType === 'facebook' || contentType === 'instagram' || contentType === 'tiktok') {
            if (newGeneratedContent.social_media_caption) {
              const captionIndex = contentType === 'facebook' ? 0 : contentType === 'instagram' ? 1 : 2;
              updated.captions = [...(prev.captions || [])];
              updated.captions[captionIndex] = newGeneratedContent.social_media_caption;
            }
          } else if (contentType === 'promotional_content') {
            if (newGeneratedContent.promotional_content) {
              updated.promotional_content = [
                {
                  type: "Social Media Post",
                  text: newGeneratedContent.promotional_content
                },
                ...(prev.promotional_content?.slice(1) || [])
              ];
            }
          } else if (contentType === 'menu_description') {
            if (newGeneratedContent.menu_description) {
              updated.promotional_content = [
                ...(prev.promotional_content?.slice(0, 1) || []),
                {
                  type: "Menu Description",
                  text: newGeneratedContent.menu_description
                },
                ...(prev.promotional_content?.slice(2) || [])
              ];
            }
          }
          
          // Update hashtags if provided
          if (newGeneratedContent.hashtags) {
            updated.hashtags = newGeneratedContent.hashtags;
          }
          
          return updated;
        });
      } else {
        throw new Error(result.error || 'Content refresh failed');
      }
      
    } catch (error) {
      console.error('Content refresh failed:', error);
      alert(`Failed to refresh ${contentType} content. Please try again.`);
    } finally {
      setRefreshingContent(prev => ({ ...prev, [contentType]: false }));
    }
  };

  // Function to handle hashtag clicks - now adds to all selected content types
  const handleHashtagClick = (hashtag) => {
    const hashtagText = `#${hashtag}`;
    
    // Get all currently selected content types
    const selectedTypes = Object.entries(selectedContentTypes)
      .filter(([_, isSelected]) => isSelected)
      .map(([type, _]) => type);
    
    if (selectedTypes.length === 0) {
      setHashtagFeedback('Please select at least one content type first!');
      setTimeout(() => setHashtagFeedback(''), 2000);
      return;
    }
    
    // Update the editable content for all selected content types
    setEditableContent(prev => {
      const updated = { ...prev };
      
      selectedTypes.forEach(contentType => {
        // Get current content using the same logic as getContentText
        let currentContent = '';
        if (updated[contentType] !== undefined) {
          currentContent = updated[contentType];
        } else {
          // Get fallback content based on content type
          if (contentType === 'facebook') {
            currentContent = generatedContent?.captions?.[0] || "🍽️ Discover amazing flavors at our restaurant! Fresh ingredients, authentic recipes, and unforgettable dining experience. Visit us today! #FreshFood #AuthenticFlavors";
          } else if (contentType === 'instagram') {
            currentContent = generatedContent?.captions?.[1] || "✨ Fresh ingredients, bold flavors, perfect moments ✨ Experience culinary excellence at its finest! 📸 #FoodieLife #RestaurantLife #FreshIngredients";
          } else {
            // For other content types, try to get from generated content or use empty string
            currentContent = '';
          }
        }
        
        const newContent = currentContent.trim()
          ? `${currentContent}\n${hashtagText}`
          : hashtagText;
        updated[contentType] = newContent;
      });
      
      return updated;
    });

    // Show feedback
    setHashtagFeedback(`Hashtag added!`);
    setTimeout(() => setHashtagFeedback(''), 2000);
  };

  // Function to handle content text changes
  const handleContentChange = (contentType, newText) => {
    setEditableContent(prev => ({
      ...prev,
      [contentType]: newText
    }));
  };

  // Function to get editable content or fallback to generated content
  const getContentText = (contentType, fallbackText) => {
    return editableContent[contentType] !== undefined
      ? editableContent[contentType]
      : fallbackText;
  };

  const deleteImage = async (imageId) => {
    // eslint-disable-next-line no-restricted-globals
    if (!confirm('Are you sure you want to delete this image?')) return;

    try {
      const result = await imageEnhancementAPI.deleteImage(imageId);
      
      if (result.success) {
        // Reload gallery
        loadImageGallery();
      } else {
        throw new Error(result.error || 'Delete request failed');
      }
    } catch (error) {
      console.error('Delete failed:', error);
      alert('Failed to delete image. Please try again.');
    }
  };

  const resetEnhancements = () => {
    setEnhancementSettings({
      brightness: 0,
      contrast: 0,
      saturation: 0,
      sharpness: 0,
      food_styling: 0
    });
  };

  return (
    <div className="image-enhancement">
      {/* Upload Section */}
      <div className="upload-section">
        <h4>📸 Upload & Enhance Images</h4>
        
        <div 
          ref={dropZoneRef}
          className={`drop-zone ${dragActive ? 'drag-active' : ''}`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          <div className="drop-zone-content">
            <div className="upload-icon">📁</div>
            <p className="upload-text">
              {selectedImage ? selectedImage.name : 'Drag & drop your image here or click to browse'}
            </p>
            <p className="upload-hint">Supports JPEG, PNG • Max 10MB</p>
          </div>
          
          <input
            ref={fileInputRef}
            type="file"
            accept="image/jpeg,image/jpg,image/png"
            onChange={handleFileInputChange}
            style={{ display: 'none' }}
          />
        </div>
        
        {/* Quick Enhancement Button - appears immediately after file selection */}
        {selectedImage && (
          <div className="quick-enhance-section">
            <button
              className={`quick-enhance-button ${loading ? 'loading' : ''}`}
              onClick={() => enhanceImage(true)}
              disabled={loading}
            >
              {loading ? '✨ Enhancing...' : '🚀 Quick Enhance Image'}
            </button>
            <p className="quick-enhance-hint">
              Click to enhance with default settings, or use advanced controls below
            </p>
          </div>
        )}
      </div>

      {/* AI Enhancement Prompts */}
      {selectedImage && (
        <div className="ai-enhancement-section">
          <h4>🤖 AI Enhancement Prompts</h4>
          
          {/* Enhanced Preset Options with Collapsible Categories */}
          <div className="preset-options">
            <h5>🎨 AI Enhancement Presets</h5>
            <p className="preset-intro">Choose from our curated collection of AI-powered enhancement presets, organized by use case:</p>
            
            <div className="presets-categories">
              {Object.entries(enhancementPresets).map(([categoryName, categoryData]) => (
                <div key={categoryName} className="preset-category">
                  <div
                    className={`category-header ${expandedCategories[categoryName] ? 'expanded' : 'collapsed'}`}
                    onClick={() => toggleCategory(categoryName)}
                    onKeyPress={(e) => handleCategoryKeyPress(e, categoryName)}
                    tabIndex={0}
                    role="button"
                    aria-expanded={expandedCategories[categoryName] || false}
                    aria-controls={`category-${categoryName.replace(/\s+/g, '-').toLowerCase()}`}
                  >
                    <div className="category-header-content">
                      <div className="category-icon">{categoryData.icon}</div>
                      <div className="category-info">
                        <h6 className="category-title">{categoryName}</h6>
                        <span className="category-description">{categoryData.description}</span>
                        <span className="category-count">({categoryData.presets.length} presets)</span>
                      </div>
                      <div className="expand-icon">
                        {expandedCategories[categoryName] ? '▼' : '▶'}
                      </div>
                    </div>
                  </div>
                  
                  <div
                    className={`category-presets ${expandedCategories[categoryName] ? 'expanded' : 'collapsed'}`}
                    id={`category-${categoryName.replace(/\s+/g, '-').toLowerCase()}`}
                  >
                    <div className="presets-grid">
                      {categoryData.presets.map(preset => (
                        <div
                          key={preset.id}
                          className={`preset-card ${selectedPreset === preset.id ? 'selected' : ''}`}
                          onClick={() => handlePresetSelection(preset)}
                        >
                          <div className="preset-icon">{preset.icon}</div>
                          <div className="preset-name">{preset.name}</div>
                          <div className="preset-description">{preset.description}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Custom Prompt Input */}
          <div className="custom-prompt-section">
            <h5>✍️ Custom Enhancement Prompt</h5>
            <div className="prompt-input-container">
              <textarea
                className="prompt-textarea"
                placeholder="Describe how you want to enhance your image... (e.g., 'Make this burger look more appetizing with warmer lighting and vibrant colors')"
                value={enhancementPrompt}
                onChange={(e) => handlePromptChange(e.target.value)}
                rows={3}
              />
              <div className="prompt-hint">
                💡 Tip: Be specific about lighting, colors, mood, or style you want to achieve
              </div>
            </div>
          </div>

          {/* Prompt Enhancement Button */}
          {enhancementPrompt.trim() && (
            <div className="prompt-enhance-section">
              <button
                className={`prompt-enhance-button ${loading ? 'loading' : ''}`}
                onClick={() => enhanceImage(false, true)}
                disabled={loading}
              >
                {loading ? '🎨 Enhancing with AI...' : '🎨 Enhance with AI Prompt'}
              </button>
              <p className="prompt-enhance-hint">
                AI will analyze your prompt and apply intelligent enhancements
              </p>
            </div>
          )}
        </div>
      )}

      {/* Enhancement Controls */}
      {originalImage && (
        <div className="enhancement-controls">
          <h4>🎨 Enhancement Controls</h4>
          
          <div className="controls-grid">
            {Object.entries(enhancementSettings).map(([key, value]) => (
              <div key={key} className="control-item">
                <label>{key.replace('_', ' ').toUpperCase()}</label>
                <div className="slider-container">
                  <input
                    type="range"
                    min="-100"
                    max="100"
                    value={value}
                    onChange={(e) => handleEnhancementChange(key, parseInt(e.target.value))}
                    className="enhancement-slider"
                  />
                  <span className="slider-value">{value}</span>
                </div>
              </div>
            ))}
          </div>

          <div className="control-buttons">
            <button 
              className="reset-button"
              onClick={resetEnhancements}
            >
              Reset All
            </button>
            <button 
              className={`enhance-button ${loading ? 'loading' : ''}`}
              onClick={enhanceImage}
              disabled={loading}
            >
              {loading ? 'Enhancing...' : '✨ Enhance Image'}
            </button>
          </div>
        </div>
      )}

      {/* Before/After Preview */}
      {originalImage && (
        <div className="preview-section">
          <h4>🔍 Image Preview</h4>
          
          <div className="preview-controls">
            <div className="zoom-controls">
              <button onClick={() => setZoomLevel(Math.max(0.5, zoomLevel - 0.25))}>-</button>
              <span>{Math.round(zoomLevel * 100)}%</span>
              <button onClick={() => setZoomLevel(Math.min(3, zoomLevel + 0.25))}>+</button>
            </div>
            
            {enhancedImage && (
              <button 
                className={`toggle-view ${showBeforeAfter ? 'active' : ''}`}
                onClick={() => setShowBeforeAfter(!showBeforeAfter)}
              >
                {showBeforeAfter ? 'Show Enhanced Only' : 'Show Before/After'}
              </button>
            )}
          </div>

          <div className={`image-preview ${showBeforeAfter ? 'before-after' : ''}`}>
            {showBeforeAfter && enhancedImage ? (
              <div className="comparison-view">
                <div className="image-container">
                  <h5>Before</h5>
                  <img 
                    src={originalImage} 
                    alt="Original" 
                    style={{ transform: `scale(${zoomLevel})` }}
                  />
                </div>
                <div className="image-container">
                  <h5>After</h5>
                  <img 
                    src={enhancedImage} 
                    alt="Enhanced" 
                    style={{ transform: `scale(${zoomLevel})` }}
                  />
                </div>
              </div>
            ) : (
              <div className="single-view">
                <img 
                  src={enhancedImage || originalImage} 
                  alt={enhancedImage ? "Enhanced" : "Original"} 
                  style={{ transform: `scale(${zoomLevel})` }}
                />
              </div>
            )}
          </div>
        </div>
      )}

      {/* Content Generation */}
      {(originalImage || enhancedImage) && (
        <div className="content-generation">
          <h4>🤖 AI Content Generation</h4>
          
          {/* Content Type Selection */}
          <div className="content-type-selection">
            <h5>📋 Select Content Types to Generate</h5>
            <div className="content-types-grid">
              <div className="content-type-item">
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={selectedContentTypes.facebook}
                    onChange={() => handleContentTypeChange('facebook')}
                  />
                  <span className="checkmark"></span>
                  <div className="content-type-info">
                    <span className="content-type-name">📘 Facebook Posts</span>
                    <span className="content-type-desc">Engaging posts for Facebook feed</span>
                  </div>
                </label>
              </div>
              
              <div className="content-type-item">
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={selectedContentTypes.instagram}
                    onChange={() => handleContentTypeChange('instagram')}
                  />
                  <span className="checkmark"></span>
                  <div className="content-type-info">
                    <span className="content-type-name">📷 Instagram Posts</span>
                    <span className="content-type-desc">Visual content for Instagram feed</span>
                  </div>
                </label>
              </div>
              
              <div className="content-type-item">
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={selectedContentTypes.tiktok}
                    onChange={() => handleContentTypeChange('tiktok')}
                  />
                  <span className="checkmark"></span>
                  <div className="content-type-info">
                    <span className="content-type-name">🎵 TikTok Content</span>
                    <span className="content-type-desc">Short-form video captions</span>
                  </div>
                </label>
              </div>
              
              <div className="content-type-item">
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={selectedContentTypes.promotional_content}
                    onChange={() => handleContentTypeChange('promotional_content')}
                  />
                  <span className="checkmark"></span>
                  <div className="content-type-info">
                    <span className="content-type-name">🎯 Promotional Content</span>
                    <span className="content-type-desc">Special offers and promotions</span>
                  </div>
                </label>
              </div>
              
              <div className="content-type-item">
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={selectedContentTypes.menu_description}
                    onChange={() => handleContentTypeChange('menu_description')}
                  />
                  <span className="checkmark"></span>
                  <div className="content-type-info">
                    <span className="content-type-name">🍽️ Menu Descriptions</span>
                    <span className="content-type-desc">Appetizing menu item descriptions</span>
                  </div>
                </label>
              </div>
              
              <div className="content-type-item">
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={selectedContentTypes.email_campaign}
                    onChange={() => handleContentTypeChange('email_campaign')}
                  />
                  <span className="checkmark"></span>
                  <div className="content-type-info">
                    <span className="content-type-name">📧 Email Campaigns</span>
                    <span className="content-type-desc">Email marketing content</span>
                  </div>
                </label>
              </div>
              
              <div className="content-type-item">
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={selectedContentTypes.google_ads}
                    onChange={() => handleContentTypeChange('google_ads')}
                  />
                  <span className="checkmark"></span>
                  <div className="content-type-info">
                    <span className="content-type-name">🔍 Google Ads</span>
                    <span className="content-type-desc">Search and display ad copy</span>
                  </div>
                </label>
              </div>
              
              <div className="content-type-item">
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={selectedContentTypes.social_media_story}
                    onChange={() => handleContentTypeChange('social_media_story')}
                  />
                  <span className="checkmark"></span>
                  <div className="content-type-info">
                    <span className="content-type-name">📱 Stories Content</span>
                    <span className="content-type-desc">Instagram/Facebook Stories</span>
                  </div>
                </label>
              </div>
              
              <div className="content-type-item">
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={selectedContentTypes.sms_campaign}
                    onChange={() => handleContentTypeChange('sms_campaign')}
                  />
                  <span className="checkmark"></span>
                  <div className="content-type-info">
                    <span className="content-type-name">📱 SMS Campaigns</span>
                    <span className="content-type-desc">Text message marketing content</span>
                  </div>
                </label>
              </div>
            </div>
          </div>
          
          <button
            className={`generate-content-button ${contentLoading ? 'loading' : ''}`}
            onClick={generateContent}
            disabled={contentLoading}
          >
            {contentLoading ? 'Generating Content...' : '🚀 Generate Marketing Content'}
          </button>
          
          <div className="content-generation-hint">
            <p>
              {enhancedImage || imageGallery.length > 0
                ? '✨ Generate AI-powered marketing content based on your enhanced image'
                : '📝 Generate general marketing content for your restaurant (upload an image for personalized content)'
              }
            </p>
          </div>

          {generatedContent && (
            <div className="generated-content">
              <div className="content-header">
                <h5>✨ Generated Content for Selected Platforms</h5>
                <div className="selected-platforms">
                  {Object.entries(selectedContentTypes)
                    .filter(([_, isSelected]) => isSelected)
                    .map(([platform, _]) => (
                      <span key={platform} className="platform-badge">
                        {platform === 'facebook' && '📘 Facebook'}
                        {platform === 'instagram' && '📷 Instagram'}
                        {platform === 'tiktok' && '🎵 TikTok'}
                        {platform === 'promotional_content' && '🎯 Promotional'}
                        {platform === 'menu_description' && '🍽️ Menu'}
                        {platform === 'email_campaign' && '📧 Email'}
                        {platform === 'google_ads' && '🔍 Google Ads'}
                        {platform === 'social_media_story' && '📱 Stories'}
                        {platform === 'sms_campaign' && '💬 SMS'}
                      </span>
                    ))}
                </div>
              </div>

              {/* Platform-specific content sections */}
              {selectedContentTypes.facebook && (
                <div className="content-section">
                  <div className="content-section-header">
                    <h5>📘 Facebook Content</h5>
                    <button
                      className={`refresh-content-button ${refreshingContent.facebook ? 'loading' : ''}`}
                      onClick={() => refreshContent('facebook')}
                      disabled={refreshingContent.facebook}
                      title="Refresh Facebook content"
                    >
                      {refreshingContent.facebook ? '🔄' : '🔄'} Refresh
                    </button>
                  </div>
                  <div className="content-grid">
                    <div className="content-item">
                      <div className="content-type">Facebook Post</div>
                      <textarea
                        className="content-textarea"
                        value={getContentText('facebook', generatedContent.captions?.[0] || "🍽️ Discover amazing flavors at our restaurant! Fresh ingredients, authentic recipes, and unforgettable dining experience. Visit us today! #FreshFood #AuthenticFlavors")}
                        onChange={(e) => handleContentChange('facebook', e.target.value)}
                        placeholder="Facebook post content..."
                        rows={4}
                      />
                      <button className="copy-button" onClick={() => navigator.clipboard.writeText(getContentText('facebook', generatedContent.captions?.[0] || "🍽️ Discover amazing flavors at our restaurant! Fresh ingredients, authentic recipes, and unforgettable dining experience. Visit us today! #FreshFood #AuthenticFlavors"))}>
                        📋 Copy
                      </button>
                    </div>
                  </div>
                </div>
              )}

              {selectedContentTypes.instagram && (
                <div className="content-section">
                  <div className="content-section-header">
                    <h5>📷 Instagram Content</h5>
                    <button
                      className={`refresh-content-button ${refreshingContent.instagram ? 'loading' : ''}`}
                      onClick={() => refreshContent('instagram')}
                      disabled={refreshingContent.instagram}
                      title="Refresh Instagram content"
                    >
                      {refreshingContent.instagram ? '🔄' : '🔄'} Refresh
                    </button>
                  </div>
                  <div className="content-grid">
                    <div className="content-item">
                      <div className="content-type">Instagram Post</div>
                      <textarea
                        className="content-textarea"
                        value={getContentText('instagram', generatedContent.captions?.[1] || "✨ Fresh ingredients, bold flavors, perfect moments ✨ Experience culinary excellence at its finest! 📸 #FoodieLife #RestaurantLife #FreshIngredients")}
                        onChange={(e) => handleContentChange('instagram', e.target.value)}
                        placeholder="Instagram post content..."
                        rows={4}
                      />
                      <button className="copy-button" onClick={() => navigator.clipboard.writeText(getContentText('instagram', generatedContent.captions?.[1] || "✨ Fresh ingredients, bold flavors, perfect moments ✨ Experience culinary excellence at its finest! 📸 #FoodieLife #RestaurantLife #FreshIngredients"))}>
                        📋 Copy
                      </button>
                    </div>
                  </div>
                </div>
              )}

              {selectedContentTypes.tiktok && (
                <div className="content-section">
                  <h5>🎵 TikTok Content</h5>
                  <div className="content-grid">
                    <div className="content-item">
                      <div className="content-type">TikTok Caption</div>
                      <div className="content-text">
                        "POV: You found the perfect spot for dinner 🔥 Fresh ingredients + amazing flavors = pure magic ✨ #FoodTok #RestaurantVibes #FreshFood #Foodie"
                      </div>
                      <button className="copy-button" onClick={() => navigator.clipboard.writeText("POV: You found the perfect spot for dinner 🔥 Fresh ingredients + amazing flavors = pure magic ✨ #FoodTok #RestaurantVibes #FreshFood #Foodie")}>
                        📋 Copy
                      </button>
                    </div>
                  </div>
                </div>
              )}

              {selectedContentTypes.promotional_content && (
                <div className="content-section">
                  <h5>🎯 Promotional Content</h5>
                  <div className="content-grid">
                    {generatedContent.promotional_content?.map((content, index) => (
                      <div key={index} className="content-item">
                        <div className="content-type">{content.type}</div>
                        <div className="content-text">{content.text}</div>
                        <button className="copy-button" onClick={() => navigator.clipboard.writeText(content.text)}>
                          📋 Copy
                        </button>
                      </div>
                    )) || (
                      <div className="content-item">
                        <div className="content-type">Special Offer</div>
                        <div className="content-text">🎉 Limited Time Offer! Get 20% off your next meal when you dine with us this week. Fresh ingredients, authentic flavors, unbeatable value! Book your table now!</div>
                        <button className="copy-button" onClick={() => navigator.clipboard.writeText("🎉 Limited Time Offer! Get 20% off your next meal when you dine with us this week. Fresh ingredients, authentic flavors, unbeatable value! Book your table now!")}>
                          📋 Copy
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {selectedContentTypes.menu_description && (
                <div className="content-section">
                  <h5>🍽️ Menu Descriptions</h5>
                  <div className="content-grid">
                    <div className="content-item">
                      <div className="content-type">Menu Item Description</div>
                      <div className="content-text">
                        "Crafted with the finest ingredients and traditional techniques, this dish delivers an authentic taste experience that will transport your senses. Fresh, flavorful, and unforgettable."
                      </div>
                      <button className="copy-button" onClick={() => navigator.clipboard.writeText("Crafted with the finest ingredients and traditional techniques, this dish delivers an authentic taste experience that will transport your senses. Fresh, flavorful, and unforgettable.")}>
                        📋 Copy
                      </button>
                    </div>
                  </div>
                </div>
              )}

              {selectedContentTypes.email_campaign && (
                <div className="content-section">
                  <h5>📧 Email Campaign Content</h5>
                  <div className="content-grid">
                    <div className="content-item">
                      <div className="content-type">Email Subject</div>
                      <div className="content-text">🍽️ Your Table Awaits - Fresh Flavors & Special Offers Inside!</div>
                      <button className="copy-button" onClick={() => navigator.clipboard.writeText("🍽️ Your Table Awaits - Fresh Flavors & Special Offers Inside!")}>
                        📋 Copy
                      </button>
                    </div>
                    <div className="content-item">
                      <div className="content-type">Email Body</div>
                      <div className="content-text">Dear Food Lover, Experience the perfect blend of fresh ingredients and authentic flavors at our restaurant. From farm-to-table freshness to time-honored recipes, every dish tells a story. Book your table today and taste the difference!</div>
                      <button className="copy-button" onClick={() => navigator.clipboard.writeText("Dear Food Lover, Experience the perfect blend of fresh ingredients and authentic flavors at our restaurant. From farm-to-table freshness to time-honored recipes, every dish tells a story. Book your table today and taste the difference!")}>
                        📋 Copy
                      </button>
                    </div>
                  </div>
                </div>
              )}

              {selectedContentTypes.google_ads && (
                <div className="content-section">
                  <h5>🔍 Google Ads Content</h5>
                  <div className="content-grid">
                    <div className="content-item">
                      <div className="content-type">Search Ad Headline</div>
                      <div className="content-text">Fresh Authentic Dining Experience</div>
                      <button className="copy-button" onClick={() => navigator.clipboard.writeText("Fresh Authentic Dining Experience")}>
                        📋 Copy
                      </button>
                    </div>
                    <div className="content-item">
                      <div className="content-type">Ad Description</div>
                      <div className="content-text">Discover exceptional flavors made with fresh ingredients. Book your table today for an unforgettable dining experience!</div>
                      <button className="copy-button" onClick={() => navigator.clipboard.writeText("Discover exceptional flavors made with fresh ingredients. Book your table today for an unforgettable dining experience!")}>
                        📋 Copy
                      </button>
                    </div>
                  </div>
                </div>
              )}

              {selectedContentTypes.social_media_story && (
                <div className="content-section">
                  <h5>📱 Stories Content</h5>
                  <div className="content-grid">
                    <div className="content-item">
                      <div className="content-type">Instagram/Facebook Story</div>
                      <div className="content-text">Behind the scenes magic ✨ Fresh ingredients becoming culinary art 🎨 Swipe up to book your table! #BehindTheScenes #FreshFood</div>
                      <button className="copy-button" onClick={() => navigator.clipboard.writeText("Behind the scenes magic ✨ Fresh ingredients becoming culinary art 🎨 Swipe up to book your table! #BehindTheScenes #FreshFood")}>
                        📋 Copy
                      </button>
                    </div>
                  </div>
                </div>
              )}

              {selectedContentTypes.sms_campaign && (
                <div className="content-section">
                  <h5>💬 SMS Campaign Content</h5>
                  <div className="content-grid">
                    <div className="content-item">
                      <div className="content-type">SMS Message</div>
                      <div className="content-text">🍽️ Fresh flavors await! Try our signature dishes made with premium ingredients. Book now & get 15% off your first visit. Reply STOP to opt out.</div>
                      <button className="copy-button" onClick={() => navigator.clipboard.writeText("🍽️ Fresh flavors await! Try our signature dishes made with premium ingredients. Book now & get 15% off your first visit. Reply STOP to opt out.")}>
                        📋 Copy
                      </button>
                    </div>
                    <div className="content-item">
                      <div className="content-type">Promotional SMS</div>
                      <div className="content-text">Limited time! 🎉 Get 20% off when you dine with us this week. Fresh ingredients, authentic flavors. Text BOOK to reserve your table!</div>
                      <button className="copy-button" onClick={() => navigator.clipboard.writeText("Limited time! 🎉 Get 20% off when you dine with us this week. Fresh ingredients, authentic flavors. Text BOOK to reserve your table!")}>
                        📋 Copy
                      </button>
                    </div>
                  </div>
                </div>
              )}

              {generatedContent.hashtags && (
                <div className="content-section">
                  <div className="hashtags-header">
                    <h5>#️⃣ Suggested Hashtags</h5>
                    <p className="hashtags-hint">Click any hashtag to add it to all selected content types!</p>
                    {hashtagFeedback && (
                      <div className="hashtag-feedback">{hashtagFeedback}</div>
                    )}
                  </div>
                  <div className="hashtags">
                    {generatedContent.hashtags.map((tag, index) => (
                      <button
                        key={index}
                        className="hashtag clickable-hashtag"
                        onClick={() => handleHashtagClick(tag)}
                        title={`Click to add #${tag} to all selected content types`}
                      >
                        #{tag}
                      </button>
                    ))}
                  </div>
                  <div className="hashtag-actions">
                    <p className="hashtag-instructions">
                      💡 Tip: Hashtags will be added to all currently selected content types above
                    </p>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Image Gallery */}
      <div className="image-gallery">
        <h4>🖼️ Your Enhanced Images</h4>
        
        {imageGallery.length === 0 ? (
          <div className="empty-gallery">
            <p>No enhanced images yet. Upload and enhance your first image!</p>
          </div>
        ) : (
          <div className="gallery-grid">
            {imageGallery.map((image) => (
              <div key={image.id || image.image_id} className="gallery-item">
                <div className="gallery-image">
                  <img
                    src={image.enhanced_url || image.original_url}
                    alt="Enhanced"
                    onError={(e) => {
                      console.log('Image failed to load:', image);
                      e.target.style.display = 'none';
                    }}
                  />
                  <div className="gallery-overlay">
                    <button
                      className="delete-button"
                      onClick={() => deleteImage(image.id || image.image_id)}
                      title="Delete image"
                    >
                      🗑️
                    </button>
                  </div>
                </div>
                <div className="gallery-info">
                  <p className="image-date">{new Date(image.created_at).toLocaleDateString()}</p>
                  <p className="image-filename">{image.original_filename}</p>
                  {image.enhancement_settings && (
                    <div className="enhancement-tags">
                      {Object.entries(image.enhancement_settings)
                        .filter(([_, value]) => value !== 0)
                        .map(([key, value]) => (
                          <span key={key} className="enhancement-tag">
                            {key}: {value > 0 ? '+' : ''}{value}
                          </span>
                        ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ImageEnhancement;